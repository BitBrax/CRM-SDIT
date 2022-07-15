# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime,date

class SaleOrder(models.Model):
	_inherit="sale.order"

	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		for order in self:
			salestarget_id =self.env['saletarget.saletarget'].search([
					('sales_person_id','=', order.sales_agent.id),
					('state','in', ['open']),
					],order="id",limit=1)
			if salestarget_id:
				rec = []
				if order.date_order.date() >= salestarget_id.start_date and order.date_order.date() <= salestarget_id.end_date:
					for order_line in order.order_line:
						for sale_line in salestarget_id.target_line_ids:
							if order_line.product_id == sale_line.product_id:
								achieve_quantity = sale_line.achieve_quantity + order_line.product_uom_qty
								rec.append((0, 0, {'product_id':order_line.product_id.id,'reference': order_line.order_id.name,'date':order_line.order_id.date_order, 'quantity': order_line.product_uom_qty, 'sale_id':order_line.order_id.id}))
								sale_line.write({'achieve_quantity': achieve_quantity})
								salestarget_id.write({'target_history_ids': rec})
					salestarget_id.update({
						'target_achieve':'Sale Order Confirm',
						'partner_id': order.partner_id.id
					})
		return res