# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError

class StockImmediateTransfer(models.TransientModel):
	_inherit = 'stock.immediate.transfer'
	_description = 'Immediate Transfer'


	def process(self):
		pickings_to_do = self.env['stock.picking']
		pickings_not_to_do = self.env['stock.picking']
		for line in self.immediate_transfer_line_ids:
			if line.to_immediate is True:
				pickings_to_do |= line.picking_id
			else:
				pickings_not_to_do |= line.picking_id

		active_id = self.env.context.get('button_validate_picking_ids')
		picking_id = self.env['stock.picking'].browse(active_id)
		if picking_id:
			sale_order_id = self.env['sale.order'].search(['|',('name','=', picking_id.origin),('name','=', picking_id.group_id.name)], limit=1)
		else:
			sale_order_id = self.env['sale.order'].search([('name','=', self.env.context.get('default_origin'))], limit=1)
		if sale_order_id:
			salestarget_id =self.env['saletarget.saletarget'].search([
					('sales_person_id','=', sale_order_id.sales_agent.id),
					('state','in', ['open']),
					],order="id",limit=1)
			if salestarget_id:
				if sale_order_id.date_order.date() >= salestarget_id.start_date and sale_order_id.date_order.date() <= salestarget_id.end_date:
					salestarget_id.update({'target_achieve':'Delivery Order Done'})

		for picking in pickings_to_do:
			# If still in draft => confirm and assign
			if picking.state == 'draft':
				picking.action_confirm()
				if picking.state != 'assigned':
					picking.action_assign()
					if picking.state != 'assigned':
						raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
			for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
				for move_line in move.move_line_ids:
					move_line.qty_done = move_line.product_uom_qty

		pickings_to_validate = self.env.context.get('button_validate_picking_ids')
		if pickings_to_validate:
			pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate)
			pickings_to_validate = pickings_to_validate - pickings_not_to_do
			return pickings_to_validate.with_context(skip_immediate=True).button_validate()
		return True