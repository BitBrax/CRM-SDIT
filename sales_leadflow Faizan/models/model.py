from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalesLead(models.Model):
    _name = 'lead.flow'
    _inherit = ['mail.thread']
    _description = 'Sale Lead Flow'

    name = fields.Char('Name', store=True)
    date = fields.Date('Date', required=True, store=True, track_visibility='onchange')
    staff_id = fields.Many2one('hr.employee', required=True, store=True, track_visibility='onchange')
    product_id = fields.Many2one('product.product', string='Product')
    campaign_id = fields.Many2one('lead.campaign', string='Campaign')
    new_lead = fields.Integer('Assigned', store=True, track_visibility='onchange')
    submitted = fields.Integer('Submitted', store=True, track_visibility='onchange')
    contacted = fields.Integer('Contacted', store=True, track_visibility='onchange')
    pending_docs = fields.Integer('Pending Docs', store=True, track_visibility='onchange')
    pending = fields.Integer('Yet to contact', compute='_get_pending', store=True)
    failed = fields.Integer('Failed', compute='_get_failed',store=True, track_visibility='onchange')
    not_contactable = fields.Integer('Not Contactable', store=True, track_visibility='onchange')
    not_eligible = fields.Integer('Not Eligible', store=True, track_visibility='onchange')
    not_interested = fields.Integer('Not Interested', store=True, track_visibility='onchange')
    rejected = fields.Integer('Rejected', store=True, track_visibility='onchange')
    closing = fields.Integer('Closing', store=True)
    call_back = fields.Integer('Call back', store=True, track_visibility='onchange')
    reactivating_base_no = fields.Char('Re-Activating Base #', store=True)
    regularized_in_branch_id = fields.Many2one('regularized.branch', store=True)
    regularized = fields.Integer('Done', store=True)
    done_percentage = fields.Integer(compute='_get_done_percentage')
    failed_percentage = fields.Integer(compute='_get_failed_percentage')
    state = fields.Selection([('draft','Draft'),('confirm','Confirm')],default='draft', track_visibility='onchange')

    @api.depends('regularized','new_lead')
    def _get_done_percentage(self):
        for record in self:
            try:
                record.done_percentage = record.regularized * 100 / record.new_lead
            except ZeroDivisionError:
                return record.done_percentage

    @api.depends('failed','new_lead')
    def _get_failed_percentage(self):
        for record in self:
            try:
                record.failed_percentage = record.failed * 100 / record.new_lead
            except ZeroDivisionError:
                return record.failed_percentage

    @api.depends('not_contactable','not_eligible','not_interested','rejected')
    def _get_failed(self):
        for rec in self:
            rec.failed = rec.not_contactable + rec.not_eligible + rec.not_interested + rec.rejected

    @api.depends('new_lead','submitted','failed','regularized')
    def _get_pending(self):
        for rec in self:
            rec.pending = rec.new_lead - rec.contacted - rec.failed - rec.regularized

    def button_confirm(self):
        return self.write({'state': 'confirm'})

    def button_reset(self):
        return self.write({'state': 'draft'})


class SaleCampaign(models.Model):
    _name = 'lead.campaign'
    _description = 'Lead Campaign'

    name = fields.Char('Name', required=True)


class BranchRegularized(models.Model):
    _name = 'regularized.branch'

    name = fields.Char('Branch Location')
    country_id = fields.Many2one('res.country')


class LeadActivity(models.Model):
    _name = 'activity.lead'
    _inherit = ['mail.thread']
    _description = 'Activity Flow'

    name = fields.Char('Name', store=True)
    activity_tye_id = fields.Many2one('do.activity', track_visibility='onchange')
    aasign_to = fields.Many2one('hr.employee', string='Staff', track_visibility='onchange')
    assigned_date = fields.Date('Assigned Date')
    due_date = fields.Date('Date Due', track_visibility='onchange')
    note = fields.Char('Note/Summary', track_visibility='onchange')
    target = fields.Integer('Target')
    achieved = fields.Integer('Achieve', track_visibility='onchange')
    state = fields.Selection([('draft','Draft'),('confirm','Confirm')], default='draft', track_visibility='onchange')

    def button_confirm(self):
        return self.write({'state':'confirm'})

    def button_reset(self):
        return self.write({'state':'draft'})


class ActivityDoing(models.Model):
    _name = 'do.activity'
    _description = 'Activity'

    name = fields.Char('Name')
    description = fields.Char('Description')


class ScheduleActivity(models.Model):
    _name = 'activity.schedule'
    _inherit = ['mail.thread']
    _description = 'Schedule Activity'

    name = fields.Char('Name', store=True, required=True)
    activity_ids = fields.One2many('activity.staff', 'staff_activity_id')
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('close', 'Close'), ('reset', 'Reset')],
                             default='draft', track_visibility='onchange')

    def check_schedule_activity(self):
        activity_record = self.env['activity.schedule'].search([],limit=1)
        print(activity_record)
        if not activity_record.activity_ids:
            raise ValidationError(_('Please define the Schedule Activity Configuration.'))
        for rec in activity_record.activity_ids:
            last_record = self.env['activity.lead'].search([('aasign_to','=',rec.staff_id.id)], order='assigned_date asc')
            if rec.activity_type == 'daily':
                self.env['activity.lead'].create({'name': rec.staff_id.name,
                                                  'activity_tye_id': rec.activity_type_id.id,
                                                  'aasign_to': rec.staff_id.id,
                                                  'assigned_date': fields.Date.today(),
                                                  'due_date':fields.Date.today(),
                                                  'target': rec.target,
                                                  'state': 'draft'})
            elif rec.activity_type == 'weekly':
                if not last_record:
                    self.env['activity.lead'].create({'name': rec.staff_id.name,
                                                      'activity_tye_id': rec.activity_type_id.id,
                                                      'aasign_to': rec.staff_id.id,
                                                      'assigned_date': fields.Date.today(),
                                                      'due_date': fields.Date.today(),
                                                      'target': rec.target,
                                                      'state': 'draft'})
                else:
                    difference = fields.Date.today() - last_record[0].assigned_date
                    if difference.days == 7:
                        self.env['activity.lead'].create({'name': rec.staff_id.name,
                                                          'activity_tye_id': rec.activity_type_id.id,
                                                          'aasign_to': rec.staff_id.id,
                                                          'assigned_date': fields.Date.today(),
                                                          'due_date':fields.Date.today(),
                                                          'target': rec.target,
                                                          'state': 'draft'})
            elif rec.activity_type == 'monthly':
                if not last_record:
                    self.env['activity.lead'].create({'name': rec.staff_id.name,
                                                      'activity_tye_id': rec.activity_type_id.id,
                                                      'aasign_to': rec.staff_id.id,
                                                      'assigned_date': fields.Date.today(),
                                                      'due_date': fields.Date.today(),
                                                      'target': rec.target,
                                                      'state': 'draft'})
                else:
                    difference = fields.Date.today() - last_record[0].assigned_date
                    if difference.days == 30:
                        self.env['activity.lead'].create({'name': rec.staff_id.name,
                                                          'activity_tye_id': rec.activity_type_id.id,
                                                          'aasign_to': rec.staff_id.id,
                                                          'assigned_date': fields.Date.today(),
                                                          'due_date':fields.Date.today(),
                                                          'target': rec.target,
                                                          'state': 'draft'})

    def button_active(self):
        return self.write({'state': 'active'})

    def button_close(self):
        return self.write({'state': 'close'})

    def button_reset(self):
        return self.write({'state': 'draft'})


class StaffActivity(models.Model):
    _name = 'activity.staff'
    _description = 'Staff Activity'

    staff_activity_id = fields.Many2one('activity.schedule')
    staff_id = fields.Many2one('hr.employee', string='Staff', required=True)
    activity_type_id = fields.Many2one('do.activity', store=True, required=True)
    activity_type = fields.Selection([('daily','Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='', required=True)
    target = fields.Integer('Target', store=True, required=True)

