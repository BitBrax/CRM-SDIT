# -*- coding: utf-8 -*-
from __future__ import division
from odoo import models, fields, api, _
import time
import calendar
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta


class EmployeeInheritBatch(models.Model):
	_inherit = 'hr.employee'

	product_sale_ids = fields.One2many('product.sales', 'prod_sale_id')
	joining_date = fields.Date('Joining Date')


class SaleProduct(models.Model):
	_name = 'product.sales'

	prod_sale_id = fields.Many2one('hr.employee', string='Product Sale')
	product_id = fields.Many2one('product.product', store=True, required=True)
	target_quantity = fields.Integer('Target Qty', store=True, required=True)
	target_quantity_monthly = fields.Integer('Monthly Target Qty', store=True, required=True)
	threshold_quantity = fields.Integer('Threshold Qty', store=True, required=True)
	threshold_quantity_monthly = fields.Integer('Monthly Threshold Qty', store=True, required=True)


class BatchSaleTarget(models.Model):
	_name = 'saletarget.batch'
	_description = 'Sales Target Batch'

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
	name = fields.Char(required=True, readonly=True, states={'draft': [('readonly', False)]})
	target_ids = fields.One2many('saletarget.saletarget', 'saletarget_batch_id', string='Sale Target')
	date_start = fields.Date(string='Date From', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
	date_end = fields.Date(string='Date To', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
	saletarget_count = fields.Integer(compute='_compute_saletarget_count')
	difference_days = fields.Integer(compute='_date_difference')

	state = fields.Selection([
		('draft', 'Draft'),
		('open', 'Open'),
		('closed', 'Closed'),
		('cancelled', 'Cancelled'),
	], string='Status', index=True, readonly=True, copy=False, default='draft')

	@api.depends('date_start', 'date_end')
	def _date_difference(self):
		for rec in self:
			if rec.date_end:
				d1 = rec.date_start
				d2 = rec.date_end
				rec.difference_days = (d2 - d1).days + 1

	def _compute_saletarget_count(self):
		for records in self:
			records.saletarget_count = len(records.target_ids)

	@api.onchange('month', 'year')
	def onchange_period(self):
		if self.month and self.year:
			start_end = calendar.monthrange(self.year, int(self.month))
			self.date_start = str(self.year) + '-' + self.month + '-01'
			self.date_end = str(self.year) + '-' + self.month + '-' + str(start_end[1])

	def confirm_batch(self):
		for record in self.target_ids:
			record.confirm()
		return self.write({'state':'open'})

	def set_draft_batch(self):
		for record in self.target_ids:
			record.set_draft()
		return self.write({'state':'draft'})

	def close_batch(self):
		for record in self.target_ids:
			record.close()
		return self.write({'state':'closed'})

	def cancel_batch(self):
		for record in self.target_ids:
			record.cancel()
		return self.write({'state':'cancelled'})

	def action_open_saletarget(self):
		self.ensure_one()
		return {
			"type": "ir.actions.act_window",
			"res_model": "saletarget.saletarget",
			"views": [[False, "tree"], [False, "form"]],
			"domain": [['id', 'in', self.target_ids.ids]],
			"name": "Sales Target",
		}


class TargetLines(models.Model):
	_inherit = 'saletarget.saletarget'

	saletarget_batch_id = fields.Many2one('saletarget.batch')


class SalesTargetByStaff(models.TransientModel):
	_name = 'saletaget.batch.salesperson'

	staff_ids = fields.Many2many('hr.employee', 'sale_employee_group_rel', 'target_id', 'staff_id', 'Staff')

	def compute_saletarget(self):
		saletarget_run = self.env['saletarget.batch'].browse(self.env.context.get('active_id'))
		staffs = self.with_context(active_test=False).staff_ids
		if not staffs:
			raise UserError(_("You must select staff(s) to generate sale target(s)."))
		saletargets = self.env['saletarget.saletarget']
		for emp in staffs:
			target_product = []
			if not emp.product_sale_ids:
				raise ValidationError(
					_("Before generating sale target, you must have to define sale target for staff %s") % (emp.name))
			for sale_target in emp.product_sale_ids:
				target_product.append((0, 0, {'product_id': sale_target.product_id.id, 'target_quantity': sale_target.target_quantity,'threshold_quantity': sale_target.threshold_quantity}))
			count = -1
			for rec in range(saletarget_run.difference_days):
				count += 1
				is_official_day = emp.resource_calendar_id.check_day_is_official_day(saletarget_run.date_start + timedelta(days=count))
				if is_official_day == True:
					saletargets.create({'sales_person_id': emp.id,
										'start_date': saletarget_run.date_start + timedelta(days=count),
										'end_date':saletarget_run.date_start + timedelta(days=count),
										'saletarget_batch_id':saletarget_run.id,
										'target_line_ids': target_product})


class InheritResource(models.Model):
	_inherit = 'resource.calendar'

	@api.model
	def check_day_is_official_day(self, day):
		# day = day is datetime and day or datetime.strptime(day, "%Y-%m-%d")
		day = type(day) == str and datetime.strptime(day, "%Y-%m-%d") or day
		week_day = day.weekday()
		week_day = week_day and week_day or '0'
		resource_calendar_attendance = self.env['resource.calendar.attendance'].search(
			[('dayofweek', '=', week_day), ('calendar_id', '=', self.id)])
		if resource_calendar_attendance:
			return True
		else:
			return False
