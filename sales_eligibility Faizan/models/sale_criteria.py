# -*- coding: utf-8 -*-
from __future__ import division
import time
import calendar
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError


class PoolSale(models.Model):
    _name = 'sale.pool'

    name = fields.Char('Name')
    percentage_in = fields.Integer('Percentage')
    percentage_out = fields.Integer('To')


class EligibilityCriteria(models.Model):
    _name = 'sale.criteria'

    _PERIOD = [
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]
    month = fields.Selection(_PERIOD, _('Month'), default=lambda s: time.strftime("%m"))
    year = fields.Integer(_('Year'), default=lambda s: float(time.strftime('%Y')))
    name = fields.Char('Name', store=True, required=True)
    start_date = fields.Date(string='Date From', required=True, readonly=True, states={'draft': [('readonly', False)]},
                             default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    end_date = fields.Date(string='Date To', required=True, readonly=True, states={'draft': [('readonly', False)]},
                           default=lambda self: fields.Date.to_string(
                               (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    product_lines = fields.One2many('criteria.lines', 'line_ids')
    overall_percentage = fields.Integer('Overall Percentage', compute='_get_overall_percentage', store=True)
    pool_id = fields.Many2one('sale.pool', string='Pool')
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('close', 'Close'), ('reset', 'Reset')],
                             default='draft')

    @api.onchange('month', 'year')
    def onchange_period(self):
        if self.month and self.year:
            start_end = calendar.monthrange(self.year, int(self.month))
            self.start_date = str(self.year) + '-' + self.month + '-01'
            self.end_date = str(self.year) + '-' + self.month + '-' + str(start_end[1])

    def button_active(self):
        if self.overall_percentage:
            pool = self.env['sale.pool'].search([('percentage_in', '>=', self.overall_percentage)],
                                                order='percentage_in asc')
            if len(pool) > 1:
                self.pool_id = pool[0].id
            else:
                self.pool_id = pool.id
        return self.write({'state': 'active'})

    def button_close(self):
        return self.write({'state': 'close'})

    def button_reset(self):
        return self.write({'state': 'draft'})

    @api.depends('product_lines')
    def _get_overall_percentage(self):
        for rec in self:
            try:
                rec.overall_percentage = round(
                    sum([line.sale_percentage for line in rec.product_lines]) / len(rec.product_lines))
            except ZeroDivisionError:
                return rec.overall_percentage

    @api.depends('overall_percentage')
    def _get_pool(self):
        for rec in self:
            if rec.overall_percentage:
                rec.pool_id = self.env['sale.pool'].search(
                    [('percentage_in', '>=', rec.overall_percentage), ('percentage_out', '<=', rec.overall_percentage)],
                    limit=1).id


class LineCriteria(models.Model):
    _name = 'criteria.lines'
    _description = 'Criteria Lines'

    line_ids = fields.Many2one('sale.criteria', 'Product Lines')
    product_id = fields.Many2one('product.product')
    target_quantity = fields.Integer('Target Quantity')
    sale_percentage = fields.Integer('Percentage %')


class SaleCompetition(models.Model):
    _name = 'sale.competition'
    _description = 'Sales Competition'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    date_start = fields.Date('Duration')
    date_end = fields.Date('End Date')
    report_type = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly')], default='daily')
    competition_line_ids = fields.One2many('competition.lines', 'competition_id')
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('close', 'Close'), ('reset', 'Reset')],
                             default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('competition.sequence') or _('New')
        result = super(SaleCompetition, self).create(vals)
        return result

    def button_close(self):
        return self.write({'state': 'close'})

    def button_reset(self):
        return self.write({'state': 'draft'})

    def button_confirm(self):
        return self.write({'state': 'active'})

    def button_get_report(self):
        lines = self.env['competition.lines'].search([('competition_id', '=', self.id)])
        for rec in lines:
            rec.unlink()
        if self.report_type == 'daily':
            d1 = self.date_start
            d2 = self.date_end
            difference_days = (d2 - d1).days + 1
            count = -1
            for record in range(difference_days):
                count += 1
                sale_agents = []
                date = self.date_start + timedelta(days=count)
                lines = self.env['saletarget.saletarget'].search(
                    [('state', 'in', ['draft', 'open']),('start_date', '=', date)])
                if lines:
                    for i in lines:
                        if i.sales_person_id.id not in sale_agents:
                            sale_agents.append(i.sales_person_id.id)
                        for record in sale_agents:
                            sp_lines = lines.filtered(lambda x: x.sales_person_id.id == record)
                            so_lines = self.env['targetline.targetline'].search(
                                [('reverse_id', 'in', [rec.id for rec in sp_lines])])
                            if not so_lines:
                                raise ValidationError(_('Cancel the Sales Target which do not have Target Lines, before generating the report'))
                            achieve_qty = 0
                            # pool = False
                            line_count = 0
                            hit_threshold = 0
                            line_point = 0
                            percent = 0
                            exclude_from_achievement = 0
                            for items in so_lines:
                                if items.product_id.is_achievement == True:
                                    if items.achieve_quantity >= items.threshold_quantity:
                                        hit_threshold += 1
                                else:
                                    exclude_from_achievement += 1
                                line_count += 1
                                achieve_qty += items.achieve_perc
                                line_point += items.points
                                percent = achieve_qty / line_count
                                pool = self.env['sale.pool'].search(
                                    [('percentage_in', '<=', percent), ('percentage_out', '>=', percent)])
                        if hit_threshold == (line_count - exclude_from_achievement):
                            employee = self.env['hr.employee'].search([('id', '=', record)])
                            if employee:
                                self.env['competition.lines'].create({
                                    'competition_id': self.id, 'date': date,
                                    'salesperson': employee.id,
                                    'achieve_quantity': achieve_qty,
                                    'overall_percent': percent,
                                    'total_point': line_point,
                                    'pool_id': pool[0].id if len(pool) > 1 else pool.id,
                                    'no_of_wins': 1 if pool else False})


class LinesCompetition(models.Model):
    _name = 'competition.lines'
    _description = 'Competition Lines'

    competition_id = fields.Many2one('sale.competition')
    date = fields.Date('Achievement Date')
    salesperson = fields.Many2one('hr.employee', string='Staff')
    staff_id = fields.Char(related='salesperson.employee_number')
    staff_job = fields.Many2one(related='salesperson.job_id')
    pool_id = fields.Many2one('sale.pool')
    overall_percent = fields.Integer('Overall %')
    total_point = fields.Integer('Total Points')
    achieve_quantity = fields.Integer('Achieve Quantity')
    target_quantity = fields.Integer('Target Quantity')
    no_of_wins = fields.Integer('No. of wins')
    payout_status = fields.Selection([('passed','Passed'),('failed','Failed')], default='')

    def check_payout_status(self):
        for rec in self:
            criteria = self.env['sale.criteria'].search([('start_date','<=',rec.date),('end_date','>=',rec.date)])
            data = []
            if not criteria:
                raise ValidationError(_('There is no criteria defined for the achievement dates'))
            for items in criteria.product_lines:
                target_achieve = self.env['targetline.targetline'].search([('salesperson_id','=',rec.salesperson.id),('start_date','>=',rec.competition_id.date_start),('end_date','<=',rec.competition_id.date_end),('product_id','=',items.product_id.id)])
                booked = 0
                if not rec.salesperson.product_sale_ids:
                    raise ValidationError(_('Please set the sale target on salesperson %s')%(rec.salesperson.name))
                for lines in rec.salesperson.product_sale_ids:
                    print(lines.product_id.name)
                    sp_lines = target_achieve.filtered(lambda x: x.product_id.id == lines.product_id.id)
                    if sp_lines:
                        for xx in sp_lines:
                            booked += xx.booked_quantity
                        print('1', booked)
                        percent = booked * 100 / lines.threshold_quantity_monthly
                        print('2', lines.threshold_quantity_monthly)
                        print('3', percent)
                        print(items.sale_percentage)
                        if percent >= items.sale_percentage:
                            data.append(1)
            if len(data) == len(criteria.product_lines):
                rec.payout_status = 'passed'
            else:
                rec.payout_status = 'failed'


class SalesKPI(models.Model):
    _name = 'sales.kpi'
    _description = 'Sales KPI Configuration'

    name = fields.Char('KPI Name', required=True, store=True)
    target = fields.Integer('Target', required=True, store=True)
    submitted = fields.Integer('Actual', required=True, store=True)

    @api.model
    def year_selection(self):
        year = 2020  # replace 2000 with your a start year
        year_list = []
        while year != 2040:  # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    year = fields.Selection(
        year_selection,
        string="Year",
        default="2022", required=True, store=True)


class TargetKPI(models.Model):
    _name = 'target.kpi'
    _description = 'Target KPI'

    _PERIOD = [
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]
    month = fields.Selection(_PERIOD, _('Month'))

    @api.model
    def year_selection(self):
        year = 2020  # replace 2000 with your a start year
        year_list = []
        while year != 2040:  # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    year = fields.Selection(
        year_selection,
        string="Year",
        default="2022", required=True, store=True)

    name = fields.Char('Name')
    salesperson_id = fields.Many2one('hr.employee', string='Responsible')
    quarter = fields.Selection([('q1', 'Q1'), ('q2', 'Q2'), ('q3', 'Q3'), ('q4', 'Q4')])
    kpi_config_id = fields.Many2one('sales.kpi')
    target = fields.Integer('Target')
    submitted = fields.Integer('Actual')
    ratio = fields.Integer(string="Ratio", compute="_get_percentage", store=True)

    @api.onchange('month')
    def get_quarter(self):
        for rec in self:
            if rec.month in ['01', '02', '03']:
                rec.quarter = 'q1'
            elif rec.month in ['04', '05', '06', ]:
                rec.quarter = 'q2'
            elif rec.month in ['07', '08', '09']:
                rec.quarter = 'q3'
            elif rec.month in ['10', '11', '12']:
                rec.quarter = 'q4'

    @api.depends('target', 'submitted')
    def _get_percentage(self):
        for temp in self:
            try:
                temp.ratio = temp.submitted * 100 / temp.target
            except ZeroDivisionError:
                return temp.ratio


class AppraisalReport(models.Model):
    _name = 'sale.target.appraisal'
    _description = 'Sale Target Appraisal'

    _PERIOD = [
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]
    month = fields.Selection(_PERIOD, _('Month'), default=lambda s: time.strftime("%m"))
    report_type = fields.Selection([('monthly','Monthly'),('quarterly','Quarterly'),('half_yearly','Half Yearly'),('annual','Annual')], default='monthly', required=True)
    year = fields.Integer(_('Year'), default=lambda s: float(time.strftime('%Y')))
    name = fields.Char('Name', store=True, required=True)
    start_date = fields.Date(string='Date From', required=True, readonly=True, states={'draft': [('readonly', False)]},
                             default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    end_date = fields.Date(string='Date To', required=True, readonly=True, states={'draft': [('readonly', False)]},
                           default=lambda self: fields.Date.to_string(
                               (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    report_lines = fields.One2many('appraisal.report.lines', 'report_line_ids')
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('close', 'Close'), ('reset', 'Reset')],
                             default='draft')

    @api.onchange('month', 'year')
    def onchange_period(self):
        if self.report_type == 'monthly':
            if self.month and self.year:
                start_end = calendar.monthrange(self.year, int(self.month))
                self.start_date = str(self.year) + '-' + self.month + '-01'
                self.end_date = str(self.year) + '-' + self.month + '-' + str(start_end[1])

    def button_generate(self):
        months = 0
        if self.report_type == 'monthly':
            months = 1
        elif self.report_type == 'quarterly':
            months = 3
        elif self.report_type == 'half_yearly':
            months = 6
        elif self.report_type == 'annual':
            months = 12
        self.report_lines = False
        line_data = self.env['targetline.targetline'].search([('start_date','>=',self.start_date),('end_date','<=',self.end_date)])
        saleperson = []
        for rec in line_data:
            if rec.salesperson_id.id not in saleperson:
                saleperson.append(rec.salesperson_id.id)
        for sp in saleperson:
            rec = line_data.filtered(lambda x:x.salesperson_id.id == sp)
            lines = []
            for line in rec.salesperson_id.product_sale_ids:
                # if not line.appraisal_quantity:
                #     raise ValidationError(_('Please define the monthly appraisal target quantity on salesperson %s') % (rec.salesperson_id.name))
                sp_lines = rec.filtered(lambda x: x.product_id.id == line.product_id.id)
                booked = 0
                if sp_lines:
                    for xx in sp_lines:
                        booked += xx.booked_quantity
                lines.append(
                    (0, 0, {'product_id': line.product_id.id, 'target_qty': int(line.appraisal_quantity)*months,
                            'achievement_qty': booked}))
            self.env['appraisal.report.lines'].create({
                'report_line_ids':self.id,
                'staff_id': rec.salesperson_id.id,
                'target_achievement': lines})

    def button_close(self):
        return self.write({'state': 'close'})

    def button_reset(self):
        return self.write({'state': 'draft'})

    def button_confirm(self):
        return self.write({'state': 'active'})


class AppraisalReportLines(models.Model):
    _name = 'appraisal.report.lines'
    _description = 'Appraisal Report Lines'

    report_line_ids = fields.Many2one('sale.target.appraisal')
    serial_no = fields.Integer(compute='_compute_get_number')
    staff_id = fields.Many2one('hr.employee', string='Emp Name')
    employee_no = fields.Char(related='staff_id.employee_number')
    sale_officer_id = fields.Many2one(related='staff_id.supervisor')
    reporting_manager_id = fields.Many2one(related='sale_officer_id.parent_id')
    department_id = fields.Many2one(related='staff_id.department_id')
    nationality = fields.Many2one(related='staff_id.country_id')
    join_date = fields.Date(related='staff_id.joining_date')
    target_achievement = fields.One2many('achievement.target.line', 'achievement_line_id')
    average_achievement = fields.Integer(compute='_get_average_achieve')
    attendance_status = fields.Selection([('good','Good'),('bad','Bad')], default='')
    warning_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='')
    task_handling = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='')
    effort_grading = fields.Integer()
    overall_rating = fields.Integer()
    comments = fields.Char()

    @api.depends('target_achievement')
    def _get_average_achieve(self):
        for record in self:
            appraisal = 0
            booked = 0
            for lines in record.target_achievement:
                booked += lines.target_qty
                appraisal += lines.achievement_qty
            try:
                record.average_achievement = appraisal * 100 / booked
                record.effort_grading = round(record.average_achievement/10)
            except ZeroDivisionError:
                return record.average_achievement

    def action_target_achievement_details(self):
        """ Returns an action with either a list view of all the valued stock moves of `self` if the
        valuation is set as manual or a list view of all the account move lines if the valuation is
        set as automated.
        """
        self.ensure_one()
        ctx = self.env.context.copy()
        action = {'name': _('Target Achievement'), 'type': 'ir.actions.act_window', 'view_type': 'form',
                  'view_mode': 'tree,form', 'context': ctx, 'target': 'new', 'res_model': 'achievement.target.line',
                  'domain': [('achievement_line_id', '=', self.id)]}
        tree_view_ref = self.env.ref('sales_eligibility.view_target_achievement_form')
        form_view_ref = self.env.ref('sales_eligibility.view_target_achievement_tree')
        action['views'] = [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')]
        return action

    @api.depends('serial_no', 'report_line_ids')
    def _compute_get_number(self):
        for order in self.mapped('report_line_ids'):
            number = 1
            for line in order.report_lines:
                line.serial_no = number
                number += 1


class TargetAchievementLines(models.Model):
    _name = 'achievement.target.line'
    _description = 'Achievement Lines'

    achievement_line_id = fields.Many2one('appraisal.report.lines')
    product_id = fields.Many2one('product.product')
    target_qty = fields.Integer()
    achievement_qty = fields.Integer()


class InheritSaleProduct(models.Model):
    _inherit = 'product.sales'

    appraisal_quantity = fields.Char(store=True, string='Appraisal Target(Monthly)')


