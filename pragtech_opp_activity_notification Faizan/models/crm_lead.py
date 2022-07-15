from odoo import _, api, exceptions, fields, models, modules
from odoo.addons.base.models.res_users import is_selection_groups
from odoo.tools import misc, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class Users(models.Model):
    """ Added new untouched menu in a 'Lead/Opptunities' notification  """
    _inherit = 'res.users'
    _description = 'Users'
    
    @api.model
    def systray_get_activities(self):
        
        #acess the fields in crm setting as Number of days
        params = self.env['ir.config_parameter'].sudo()
        no_of_days = int(params.get_param('pragtech_opp_activity_notification.no_of_days', default=0))
        date_N_days_ago = datetime.now() - timedelta(days=no_of_days)
        crm_lead_list=[]
        crm_lead_objs=self.env['crm.lead'].search([('user_id','=',self.env.user.id),('active','=',True)])
        for crm_lead_obj in crm_lead_objs:
                activity_objs=self.env['mail.activity'].search([('res_model','=','crm.lead'),('res_id','=',crm_lead_obj.id)])
                if activity_objs:
                    if len(activity_objs)>1:
                        due_date=[]
                        for activity_obj in activity_objs:
                            due_date.append((activity_obj.date_deadline))
                        if max(due_date)<date_N_days_ago.date():
                            crm_lead_list.append(crm_lead_obj.id)
                            crm_lead_obj.sudo().write({'untouch_flag':True})
                    else:
                        if activity_objs.date_deadline<date_N_days_ago.date():
                            crm_lead_list.append(crm_lead_obj.id)
                            crm_lead_obj.sudo().write({'untouch_flag':True})
                else:
                    if crm_lead_obj.create_date<date_N_days_ago:
                        crm_lead_list.append(crm_lead_obj.id)
                        crm_lead_obj.sudo().write({'untouch_flag':True})
        
        #for all untouch_slag =flase 
        crm_lead_obj_news=self.env['crm.lead'].search([])
        for crm_lead_obj_new in crm_lead_obj_news:
            if crm_lead_obj_new.id not in list(set(crm_lead_list)):
                crm_lead_obj_new.sudo().write({'untouch_flag':False})
        
        #override default mail activity method        
        activities = super(Users, self).systray_get_activities()
        if activities ==[]:
            activities=[{'name': 'Lead/Opportunity', 'overdue_count': 0, 'icon': '/crm/static/description/icon.png', 'type': 'activity', 'model': 'crm.lead', 'total_count': 0, 'planned_count': 0, 'today_count': 0}]
        if len(list(set(crm_lead_list)))>0:
            conut_total=len(list(set(crm_lead_list)))
            if activities:
                activities[0].update({'untouch_lead':conut_total})
        return activities


class CrmLead(models.Model):
    _inherit='crm.lead'
 
    untouch_flag=fields.Boolean(store=True,default=0)
