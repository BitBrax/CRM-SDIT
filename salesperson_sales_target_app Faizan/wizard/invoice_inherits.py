# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleAdvancePaymentInv(models.TransientModel):
	_inherit = "sale.advance.payment.inv"
	_description = "Sales Advance Payment Invoice"

	def create_invoices(self):
		res = super(SaleAdvancePaymentInv, self).create_invoices()
		if res:
			if self._context.get('active_model') == 'sale.order' and self._context.get('active_id', False):
				sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
			else:
				sale_order = self.env['sale.order'].browse(self._context.get('active_ids', []))
			if sale_order:
				salestarget_id =self.env['saletarget.saletarget'].search([
						('sales_person_id','=', sale_order.sales_agent.id),
						('state','in', ['open']),
						],order="id",limit=1)
				if salestarget_id:
					if sale_order.date_order.date() >= salestarget_id.start_date and sale_order.date_order.date() <= salestarget_id.end_date:
						salestarget_id.write({'target_achieve':'Invoice Created'})
		return res
