# -*- coding: utf-8 -*-
from __future__ import division
from odoo import models, fields, api, _
from datetime import datetime,date
from odoo.exceptions import UserError


class InheritProduct(models.Model):
	_inherit = 'product.template'

	points = fields.Float(string='Points on Target Achievement')
	incentive_pay = fields.Float(string='Incentive Pay')
	is_achievement = fields.Boolean(default=False)
	saletarget_config_ids = fields.One2many('saletarget.config', 'target_id')


class ConfigSaleTarget(models.Model):
	_name = 'saletarget.config'

	target_id = fields.Many2one('product.product', 'Target')
	job_position = fields.Many2one('hr.job', string='Designation', store=True, required=True)
	target = fields.Integer('Target Value', store=True, required=True)
	threshold_percent = fields.Integer('Threshold %', store=True, required=True)
	threshold_quantity = fields.Integer('Threshold Quantity', compute='_get_quantity', store=True, required=True)

	@api.depends('target','threshold_percent')
	def _get_quantity(self):
		for lines in self:
			lines.threshold_quantity = round(lines.target * lines.threshold_percent)/100


class SaleTarget(models.Model):
	_name = "saletarget.saletarget"
	_description = "Sales Target"

	name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
	sales_person_id = fields.Many2one('hr.employee',string="Salesperson")
	sales_staff_id = fields.Char(related='sales_person_id.employee_number')
	manager_id = fields.Many2one(related='sales_person_id.parent_id')
	supervisor_id = fields.Many2one(related='manager_id.parent_id')
	start_date = fields.Date(string="Start Date")
	end_date = fields.Date(string="End Date")
	target_achieve = fields.Selection([('Sale Order Confirm','Sale Order Confirm'),
								('Delivery Order Done','Delivery Order Done'),
								('Invoice Created','Invoice Created'),
								('Invoice Paid','Invoice Paid')],string="Target Achieve")
	target = fields.Integer(string="Target")
	difference = fields.Integer(string="Difference",compute="_get_difference",store=True, readonly=True)
	average = fields.Float(string="Average Achievement", compute="_get_difference", store=True, readonly=True)
	total_points = fields.Float(string="Total Points", compute="_get_points", store=True, readonly=True)
	achieve = fields.Integer(string="Achieve", compute="_compute_sales_target", store=True, readonly=True)
	achieve_percentage = fields.Integer(string="Achieve Percentage",compute="_get_achieve_percentage", readonly=True)
	average_percentage = fields.Integer(string="Overall Submission %", compute="_get_average_percentage", readonly=True)
	booked_percentage = fields.Integer(string="Overall Booked %", compute="_get_booked_avg_percentage", readonly=True)
	responsible_salesperson_id = fields.Many2one('res.users',string="Responsible Salesperson")
	target_line_ids = fields.One2many('targetline.targetline','reverse_id')
	target_history_ids = fields.One2many('targetline.history', 'history_id')
	saletarget_batch_id = fields.Many2one('saletarget.batch', 'Batch Name')
	state = fields.Selection([
			('draft','Draft'),
			('open', 'Open'),
			('closed', 'Closed'),
			('cancelled', 'Cancelled'),
		], string='Status', readonly=True, default='draft')
	partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('saletarget.sequence') or _('New')
		result = super(SaleTarget, self).create(vals)
		return result

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise UserError(_('You can only delete an sales target in draft state.'))
		return super(SaleTarget, self).unlink()

	def confirm(self):
		for record in self:
			record.target = sum([line.target_quantity for line in record.target_line_ids])
		for j in self.target_line_ids:
			j.salesperson_id = record.sales_person_id.id
			j.start_date = record.start_date
			j.end_date = record.end_date
			j.salesperson_employee_no = record.sales_staff_id
			j.manager_id = record.manager_id.id
			j.supervisor_id = record.manager_id.parent_id.id
		return self.write({'state':'open'})

	def set_draft(self):
		return self.write({'state':'draft'})

	def close(self):
		return self.write({'state':'closed'})

	def cancel(self):
		return self.write({'state':'cancelled'})

	@api.depends('target_line_ids','target_line_ids.achieve_quantity')
	def _compute_sales_target(self):
		for record in self:
			record.achieve = sum([line.achieve_quantity for line in record.target_line_ids])

	@api.depends('target_line_ids', 'target_line_ids.points')
	def _get_points(self):
		for record in self:
			record.total_points = sum([line.points for line in record.target_line_ids])

	@api.depends('achieve','target')
	def _get_achieve_percentage(self):
		for record in self:
			try:
				record.achieve_percentage = record.achieve * 100/record.target
			except ZeroDivisionError:
				return record.achieve_percentage

	@api.depends('target_line_ids')
	def _get_average_percentage(self):
		for rec in self:
			try:
				rec.average_percentage = sum([line.achieve_perc for line in rec.target_line_ids])/len(rec.target_line_ids)
			except ZeroDivisionError:
				return rec.average_percentage

	@api.depends('target_line_ids')
	def _get_booked_avg_percentage(self):
		for rec in self:
			try:
				rec.booked_percentage = sum([line.booked_percentage for line in rec.target_line_ids])/len(rec.target_line_ids)
			except ZeroDivisionError:
				return rec.booked_percentage

	@api.depends('achieve','target','target_line_ids')
	def _get_difference(self):
		for items in self:
			items.difference = items.target - items.achieve
			if items.target_line_ids:
				items.average = items.achieve / len(items.target_line_ids)

	def send_mail(self):
		template_id = self.env['ir.model.data'].get_object_reference('salesperson_sales_target_app','sales_person_send_mail')[1]
		email_template_obj = self.env['mail.template'].browse(template_id)
		if template_id:
			values = email_template_obj.generate_email(self.id, fields=None)
			values['email_from'] = self.env.user.email
			values['email_to'] = self.sales_person_id.partner_id.email
			values['author_id'] = self.env.user.partner_id.id
			mail_mail_obj = self.env['mail.mail']
			msg_id = mail_mail_obj.sudo().create(values)
			if msg_id:
				msg_id.sudo().send()


class TargetLine(models.Model):
	_name = "targetline.targetline"
	_description = "Sales Target Line"

	name = fields.Char(string="Name")
	salesperson_id = fields.Many2one('hr.employee')
	manager_id = fields.Many2one('hr.employee')
	supervisor_id = fields.Many2one('hr.employee')
	salesperson_employee_no = fields.Char('Staff ID')
	reverse_id = fields.Many2one('saletarget.saletarget')
	start_date = fields.Date('Start date')
	end_date = fields.Date('End date')
	product_id = fields.Many2one('product.product', string="Product", required=True)
	target_quantity = fields.Integer(string="Target", required=True)
	threshold_quantity = fields.Integer(string="Threshold", required=True)
	achieve_quantity = fields.Integer(string="Submitted")
	projected_quantity = fields.Integer(string="Projected")
	booked_quantity = fields.Integer(string="Booked")
	difference = fields.Integer(string='Variance', compute="_get_difference")
	returned_quantity = fields.Integer(string='Returned')
	incentive_unit_product = fields.Float(related='product_id.incentive_pay', string='Incentive/Unit Product', store=True)
	achieve_perc = fields.Integer(string="Submission %", compute="_get_percentage",store=True)
	booked_percentage = fields.Integer(string="Booked %", compute="_get_booked_percentage", store=True)
	projected_percentage = fields.Integer(string="Projected %", compute="_get_projected_percentage", store=True)
	incentive_pay = fields.Float(string='Incentives Pay Out', compute='_get_incentive_amount', store=True)
	points = fields.Float(string='Points', compute='_get_incentive_amount', store=True)
	points_per_products = fields.Float(related='product_id.points', string='Points/Unit', store=True)

	@api.depends('target_quantity','achieve_quantity','returned_quantity')
	def _get_difference(self):
		for lines in self:
			lines.difference = (lines.target_quantity - lines.achieve_quantity) + lines.returned_quantity

	@api.depends('target_quantity', 'booked_quantity')
	def _get_booked_percentage(self):
		for temp in self:
			try:
				temp.booked_percentage = temp.booked_quantity * 100/temp.target_quantity
			except ZeroDivisionError:
				return temp.booked_percentage

	@api.depends('projected_quantity', 'booked_quantity')
	def _get_projected_percentage(self):
		for temp in self:
			try:
				temp.projected_percentage = temp.booked_quantity * 100/temp.projected_quantity
			except ZeroDivisionError:
				return temp.projected_percentage

	@api.depends('target_quantity','achieve_quantity')
	def _get_percentage(self):
		for temp in self:
			try:
				temp.achieve_perc = temp.achieve_quantity * 100/temp.target_quantity
			except ZeroDivisionError:
				return temp.achieve_perc

	@api.depends('target_quantity', 'threshold_quantity', 'achieve_quantity', 'incentive_unit_product','points_per_products','returned_quantity')
	def _get_incentive_amount(self):
		for lines in self:
			# returned = lines.returned_quantity
			# print(returned)
			# if lines.returned_quantity:
			# 	print(lines.returned_quantity)
			# 	lines.achieve_quantity = (lines.achieve_quantity - (lines.returned_quantity - returned))
			if lines.achieve_quantity >= lines.threshold_quantity:
				lines.incentive_pay = lines.achieve_quantity * lines.incentive_unit_product
			else:
				lines.incentive_pay = 0.0
			if lines.achieve_quantity >= lines.target_quantity:
				lines.points = lines.points_per_products
			else:
				lines.points = 0.0

	@api.onchange('product_id')
	def get_salesperson(self):
		for rec in self:
			if rec.product_id:
				rec.salesperson_id = rec.reverse_id.sales_person_id.id
				rec.salesperson_employee_no = rec.reverse_id.sales_person_id.employee_number
				rec.start_date = rec.reverse_id.start_date
				rec.end_date = rec.reverse_id.end_date
				if rec.product_id.saletarget_config_ids:
					for lines in rec.product_id.saletarget_config_ids:
						if rec.salesperson_id.job_id.id == lines.job_position.id:
							rec.target_quantity = lines.target
							rec.threshold_quantity = lines.threshold_percent


class TargetHistory(models.Model):
	_name = "targetline.history"
	_description = "Target Line History"

	name = fields.Char(string="Name")
	sale_id = fields.Many2one('sale.order')
	history_id = fields.Many2one('saletarget.saletarget')
	product_id = fields.Many2one('product.product', string="Product")
	date = fields.Date('Date')
	reference = fields.Char('Reference')
	quantity = fields.Float('Quantity')

