# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime,date

class AccountPaymentRegister(models.TransientModel):
	_inherit = 'account.payment.register'
	_description = 'Register Payment'

	def action_create_payments(self):
		res = super(AccountPaymentRegister, self).action_create_payments()
		if res:
			if self._context.get('active_model') == 'account.move' and self._context.get('active_id', False):
				account_move = self.env['account.move'].browse(self._context.get('active_id'))
			else:
				account_move = self.env['account.move'].browse(self._context.get('active_ids', []))
			if account_move:
				sale_order_id = self.env['sale.order'].search([('name','=', account_move.invoice_origin)], limit=1)
				if sale_order_id:
					salestarget_id =self.env['saletarget.saletarget'].search([
							('sales_person_id','=', sale_order_id.sales_agent.id),
							('state','in', ['open']),
							],order="id",limit=1)
					if salestarget_id:
						if sale_order_id.date_order.date() >= salestarget_id.start_date and sale_order_id.date_order.date() <= salestarget_id.end_date:
							salestarget_id.write({'target_achieve':'Invoice Paid'})
		return res
