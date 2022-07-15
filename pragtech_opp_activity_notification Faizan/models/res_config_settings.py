from odoo import api, models, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    no_of_days = fields.Integer('No of days', readonly=False
        , help="Number of days untouched activity on crm lead")
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['no_of_days'] = int(self.env['ir.config_parameter'].sudo().get_param('pragtech_opp_activity_notification.no_of_days', default=0)) 
        return res
    
    #@api.multi
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('pragtech_opp_activity_notification.no_of_days', self.no_of_days)
        super(ResConfigSettings, self).set_values()
