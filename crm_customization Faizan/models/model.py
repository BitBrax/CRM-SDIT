from odoo import models, fields, api, _
from datetime import date, datetime, time
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import datetime
from datetime import timedelta


class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    employee_number = fields.Char('Employee Number')
    supervisor = fields.Many2one('hr.employee', 'Manager')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    building_no = fields.Char('Building No')
    additional_no = fields.Char('Additional No')
    other_seller_id = fields.Char('Other Seller Id')


class InheritCRMStage(models.Model):
    _inherit = 'crm.stage'

    is_allocate = fields.Boolean(default=False, string="Meeting Schedule")
    is_reviewed = fields.Boolean(default=False, string="Pending Contact")
    is_rejected = fields.Boolean(default=False)
    is_accepted = fields.Boolean(default=False, string='With QVC Team')
    is_card = fields.Boolean(default=False, string='Submitted Lead')


class InheritCRM(models.Model):
    _inherit = 'crm.lead'

    account_no = fields.Char(store=True)
    arrival_status_tag = fields.Many2many('arrival.status')
    arrival_status = fields.Selection([('yes','Yes'),('no','No')],default='', string='Arrived in Qatar?')
    qvc_staff = fields.Many2one('hr.employee', string='Staff')
    applicant_name = fields.Char(store=True)
    father_name = fields.Char(string='Father/Husband Name', store=True)
    passport_no = fields.Char('Passport Number')
    passport_expiry = fields.Date('Passport Expiry Date')
    profession_abroad = fields.Char('Profession Abroad')
    passport_attachment = fields.Binary(store=True, index=True)
    salary_attachment = fields.Binary(store=True, index=True)
    qid_attachment = fields.Binary(store=True, index=True)
    offer_letter_attachment = fields.Binary(store=True, index=True)
    fatch_form_attachment = fields.Binary(store=True, index=True)
    employer_id = fields.Many2one('res.partner')
    street_work = fields.Char('Street', store=True)
    street2_work = fields.Char('Street2', store=True)
    zip_work = fields.Char('Zip', store=True)
    city_work = fields.Char('City', store=True)
    state_id_work = fields.Many2one("res.country.state", string='State', store=True)
    country_id_work = fields.Many2one('res.country', string='Country', store=True)
    flat_no_work = fields.Char('Flat No.',store=True)
    building_work = fields.Char('Building No.', store=True)
    street_home = fields.Char('Street', store=True)
    street2_home = fields.Char('Street2', store=True)
    zip_home = fields.Char('Zip', store=True)
    city_home = fields.Char('City', store=True)
    state_id_home = fields.Many2one("res.country.state", string='State', store=True)
    country_id_home = fields.Many2one('res.country', string='Country', store=True)
    flat_no_home = fields.Char('Flat No.',store=True)
    building_home = fields.Char('Building No.', store=True)
    street_home_na = fields.Char('Street', store=True)
    street2_home_na = fields.Char('Street2', store=True)
    zip_home_na = fields.Char('Zip', store=True)
    city_home_na = fields.Char('City', store=True)
    state_id_home_na = fields.Many2one("res.country.state", string='State', store=True)
    country_id_home_na = fields.Many2one('res.country', string='Country', store=True)
    flat_no_home_na = fields.Char('Flat No.',store=True)
    building_home_na = fields.Char('Building No.', store=True)
    is_blacklisted = fields.Boolean(default=False)
    monthly_salary = fields.Float(store=True)
    other_income = fields.Float(store=True)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True)
    email_con = fields.Char(string='Email', store=True)
    mobile_con = fields.Char(string='Phone', store=True)
    country_phone = fields.Char(string='Country Phone', store=True)
    has_info = fields.Boolean(default=False)
    has_docs = fields.Boolean(default=False)
    has_travel_info = fields.Boolean(default=False)
    has_sa = fields.Boolean(default=False)
    age = fields.Float(string='Age', compute='get_age', store=True)
    emergency_contact = fields.Char(string='Alternative Contact', store=True)
    birthday = fields.Date('Date of Birth(Geogorian)', groups="hr.group_hr_user", required=False)
    place_of_birth = fields.Char('Place of Birth', groups="hr.group_hr_user", required=False)
    country_of_birth = fields.Many2one('res.country', string="Country of Birth", groups="hr.group_hr_user",
                                       required=False)
    nationality = fields.Many2one('res.country', 'Nationality')
    nationality_type = fields.Selection([('Native', 'Native'),('Non-native', 'Non-native')], 'Nationality type')
    identification_no = fields.Char('Identification No.', groups="hr.group_hr_user")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="hr.group_hr_user", default="male", required=False)
    language = fields.Char(string="Language", groups="hr.group_hr_user")
    additional_service = fields.Selection([('yes','Yes'),('no','No')],default='no')
    exchange_card = fields.Boolean(default=False)
    consumer_loan = fields.Boolean(default=False)
    vehicle = fields.Boolean(default=False)
    insurance = fields.Boolean(default=False)
    loan_purpose = fields.Char('Purpose of loan')
    loan_amount = fields.Char('Loan amount')
    martial_status = fields.Selection([('single','Single'),('married','Married')],default='single', string='Martial Status')
    no_of_dependent = fields.Integer('No of Dependents')
    degree_level = fields.Selection([('matric','Matric'),('intermediate','Intermediate'),('bachelors','Bachelors'),('masters','Masters')],default='', string='Degree Level')
    employment_status = fields.Selection([('employed','Employed'),('unemployed','Unemployed')],default='', string='Employment Status')
    occupation = fields.Char(string='Occupation')
    organization_name = fields.Char(string='Organization')
    monthly_income = fields.Char('Monthly Income', compute='calc_income', store=True)
    service_duration = fields.Char('Service Duration')
    vehicle_type = fields.Char('Vehicle Type')
    have_license = fields.Boolean('Have license?')
    license_no = fields.Char('Vehicle No')
    license_expiry = fields.Date('License Expiry')
    is_reviewed = fields.Boolean(default=False)
    is_allocated = fields.Boolean(default=False)
    is_accepted = fields.Boolean(default=False)
    is_rejected = fields.Boolean(default=False)
    is_sa_info = fields.Boolean(default=False)
    reject_reason = fields.Char('Reject Reason')
    operation_state = fields.Selection([('draft','Draft'),('submit','Submitted'),('reviewed','Reviewed'),('approved','Approved'),('returned','Returned'),('rejected','Rejected'),
                                        ('cpv_failed','CPV Failed'),('cpv_pending','CPV Pending'),('sent_for_prod','Sent for Production'),('delivered','Delivered'),('pending','Pending Activation')], default='draft')
    client_id = fields.Many2one('res.partner', string='Client')
    service_type = fields.Selection(
        [('ec', 'ECard (Wallet)'), ('cl', 'Consumer Loan'), ('vehicle', 'Vehicle'), ('insurance', 'Insurance')],
        default='')
    is_service_request = fields.Boolean(default=False)
    dcard_number = fields.Char(store=True)
    airline_agency = fields.Char(store=True)
    flight_reference = fields.Char(store=True)
    arrival_time = fields.Datetime(store=True, track_visibility='always')
    departure_city = fields.Char(store=True)
    arrival_city = fields.Char(store=True)
    sales_agent = fields.Many2one('hr.employee', string='Sales Agent',store=True, track_visibility='always')
    sales_manager_id = fields.Many2one('hr.employee', string='Sales Manager', store=True, track_visibility='always')
    sales_officer_id = fields.Many2one('hr.employee', string='Sales Officer', store=True, track_visibility='always')
    sales_officer_emp_no = fields.Char(related='sales_officer_id.employee_number')
    sales_officer_department = fields.Many2one(related='sales_officer_id.department_id')
    sales_agent_id = fields.Char(related='sales_agent.employee_number')
    sales_officer = fields.Many2one(related='sales_agent.parent_id')
    sales_department = fields.Many2one(related='sales_agent.department_id')
    sales_deadline = fields.Date(string='Last Day Month', default=datetime.date.today()+timedelta(days=2),track_visibility='always')
    digital_signature_attach = fields.Binary('Digital Signature Form')
    contacting_date = fields.Date('Contacting Date',track_visibility='always')
    request_card = fields.Boolean(default=False,track_visibility='always')
    account_op_form = fields.Binary('Account Opening Form')
    dcard_form = fields.Binary('Digital Card Form')
    undertaking_form = fields.Binary('Undertaking Letter')
    has_client = fields.Boolean(default=False)
    has_application = fields.Boolean(default=False)
    unlocked = fields.Boolean(default=False)
    meeting_date = fields.Date(string='Meeting Date',track_visibility='always')
    is_card_deliver = fields.Boolean(default=False,track_visibility='always')
    passport_copy = fields.Binary(store=True)
    is_glass_sign = fields.Boolean(default=False)
    lead_submission_date = fields.Date(string='Submission Date',track_visibility='always')
    campaign_ids = fields.Many2many('lead.campaign')
    amount_limit = fields.Float('Limit', store=True)
    tenor = fields.Char('Tenor', store=True)

    _sql_constraints = [
        ('unique_account_no', "unique(account_no)", "Active Base Number must be unique."),
    ]

    def proceed_request(self):
        self.stage_id = self.env['crm.stage'].search([('is_accepted','=',True)]).id
        self.is_accepted = True
        self.has_info = True

    def proceed_with_qvc(self):
        if self.arrival_status == 'no':
            raise ValidationError(_('Can not be proceed, until arrival of client. Please mention the Arrival date and Airline agency'))
        self.stage_id = self.env['crm.stage'].search([('is_reviewed','=',True)]).id
        self.is_reviewed = True
        self.has_docs = True

    def proceed_allocation(self):
        self.stage_id = self.env['crm.stage'].search([('is_allocate', '=', True)]).id
        self.is_allocated = True
        self.has_travel_info = True

    def proceed_lead_submit(self):
        self.stage_id = self.env['crm.stage'].search([('is_card', '=', True)]).id
        self.is_sa_info = True
        self.has_sa = True

    def button_unlock(self):
        return self.write({'is_sa_info': False,
                           'is_allocated': False,
                           'is_reviewed': False,
                           'is_accepted': False,
                           'unlocked': True})

    def button_lock(self):
        return self.write({'is_sa_info': True,
                           'is_allocated': True,
                           'is_reviewed': True,
                           'is_accepted': True,
                           'unlocked': False})

    @api.depends('birthday')
    def get_age(self):
        res = {}
        for rec in self:
            if rec.birthday:
                birthday = rec.birthday
                age_calc = (datetime.date.today() - birthday).days / 365
                age = str(age_calc)
                rec.age = age

    @api.depends('monthly_salary','other_income')
    def calc_income(self):
        for record in self:
            if record.monthly_salary:
                record.monthly_income = record.monthly_salary + record.other_income

    def create_customer(self):
        if self.name:
            customer_exist = self.env['res.partner'].search([('name','=',self.name)])
            if customer_exist:
                return
            else:
                client = self.env['res.partner'].create({'name': self.name, 'type': 'contact',
                                                         'mobile': self.mobile_con, 'email': self.email_con,
                                                         'street':self.street_work, 'street2':self.street2_work,
                                                         'city':self.city_work, 'state_id': self.state_id_work.id,
                                                         'country_id':self.country_id_work.id, 'zip':self.zip_work,
                                                         'building_no':self.building_work, 'additional_no':self.flat_no_work})
                self.client_id = client.id
                self.has_client = True

    # def action_set_won_rainbowman(self):
    #     self.create_customer()
    #     # self.button_send_mail()
    #     res = super(InheritCRM,self).action_set_won_rainbowman()
    #     return res

    def submit_operation(self):
        rec = []
        product = self.env['product.product'].search([('name','=','Account Opening')])
        if not product:
            raise ValidationError(_('Kindly add the product of Account opening.'))
        rec.append((0, 0, {'product_id': product.id}))
        application = self.env['sale.order'].create({'partner_id': self.client_id.id,
                                                     'order_line': rec})
        application.get_personal_data()
        self.has_application = True

    def action_open_request(self):
        return {
            'name': _('Applications'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('partner_id', '=', self.client_id.id)],
        }

    def action_open_contact(self):
        return {
            'name': _('Contact'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.client_id.id)],
        }

    def print_pdf_report(self):
        return self.env.ref('crm_customization.action_service_report').report_action(self)

    def button_send_mail(self):
        email_list = []
        if not self.user_id.email:
            raise ValidationError(_('Kindly configure the email on Salesperson.'))
        else:
            email_list.append(self.user_id.email)
        if not self.sales_agent.work_email:
            raise ValidationError(_('Kindly configure the email on sale agent.'))
        else:
            email_list.append(self.sales_agent.work_email)
        if not self.sales_agent.parent_id.work_email:
            raise ValidationError(_('Kindly configure the email on Manager of sales agent.'))
        else:
            email_list.append(self.sales_agent.parent_id.work_email)
        for user in email_list:
            self.action_send_prod_email(user)

    def action_send_prod_email(self,email_to):
        template_id = self.env.ref('crm_customization.email_template_contact_client').id
        template = self.env['mail.template'].browse(template_id)
        template.write({'email_to': email_to})
        template.send_mail(self.id,force_send=True)


class RejectReason(models.TransientModel):
    _name = 'request.reject'
    reason_for_rejection = fields.Text(string='Reason')

    def submit_reason(self):
        rec = self.env['sale.order'].search([('id', '=', self._context['active_id'])])
        rec.reject_reason = self.reason_for_rejection
        rec.is_rejected = True
        rec.state = 'rejected'


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    service_type_id = fields.Many2one('service.type', store=True)
    reject_reason = fields.Char('Reject Reason', index=True, tracking=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('sent', 'Quotation Sent'),
        ('submitted','Checked'),('reviewed','Reviewed'),
        ('returned','Returned'),('rejected','Rejected'),
        ('cpv_failed','CPV Failed'),('cpv_pending','CPV Pending'),
        ('sent_for_prod','Sent for Production'),('delivered','Delivered'),('pending','Pending Activation'),
        ('sale', 'Approved'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    account_no = fields.Char(string='Account Number', store=True)
    reviewed_by_tl = fields.Boolean(default=False)
    reviewed_by_sm = fields.Boolean(default=False)
    applicant_name = fields.Char(string='Applicant Name',store=True)
    passport_no = fields.Char('Present Passport Number')
    employer_id = fields.Many2one('res.partner')
    passport_expiry = fields.Date('Passport Expiry Date')
    email_con = fields.Char(string='Email', store=True)
    mobile_con = fields.Char(string='Mobile', store=True)
    age = fields.Float(string='Age', compute='get_age', store=True)
    birthday = fields.Date('Date of Birth(Geogorian)', groups="hr.group_hr_user", required=False)
    nationality = fields.Many2one('res.country', 'Nationality')
    martial_status = fields.Selection([('single','Single'),('married','Married')],default='single', string='Martial Status')
    no_of_dependent = fields.Integer('No of Dependents')
    degree_level = fields.Selection([('matric','Matric'),('intermediate','Intermediate'),('bachelors','Bachelors'),('masters','Masters')],default='', string='Degree Level')
    monthly_income = fields.Char('Monthly Income')
    is_blacklisted = fields.Boolean(default=False)
    is_rejected = fields.Boolean(default=False)
    street_work = fields.Char('Street', store=True)
    street2_work = fields.Char('Street2', store=True)
    zip_work = fields.Char('Zip', store=True)
    city_work = fields.Char('City', store=True)
    state_id_work = fields.Many2one("res.country.state", string='State', store=True)
    country_id_work = fields.Many2one('res.country', string='Country', store=True)
    flat_no_work = fields.Char('Flat No.',store=True)
    building_work = fields.Char('Building No.', store=True)
    street_home = fields.Char('Street', store=True)
    street2_home = fields.Char('Street2', store=True)
    zip_home = fields.Char('Zip', store=True)
    city_home = fields.Char('City', store=True)
    state_id_home = fields.Many2one("res.country.state", string='State', store=True)
    country_id_home = fields.Many2one('res.country', string='Country', store=True)
    flat_no_home = fields.Char('Flat No.',store=True)
    building_home = fields.Char('Building No.', store=True)
    monthly_salary = fields.Float(store=True)
    other_income = fields.Float(store=True)
    dcard_number = fields.Char(store=True)
    airline_agency = fields.Char(store=True)
    flight_reference = fields.Char(store=True)
    arrival_time = fields.Datetime(store=True)
    departure_city = fields.Char(store=True)
    arrival_city = fields.Char(store=True)
    sales_agent = fields.Many2one('hr.employee', string='Sales Agent')
    sales_agent_id = fields.Char(related='sales_agent.employee_number')
    sales_officer = fields.Many2one(related='sales_agent.parent_id')
    sales_department = fields.Many2one(related='sales_agent.department_id')
    sales_deadline = fields.Date(string='Last Day Month', default=datetime.date.today()+timedelta(days=2))
    digital_signature_attach = fields.Binary('Digital Signature Form')
    account_op_form = fields.Binary('Account Opening Form')
    dcard_form = fields.Binary('Digital Card Form')
    undertaking_form = fields.Binary('Undertaking Letter')
    passport_attachment = fields.Binary(store=True, index=True)
    fatch_form_attachment = fields.Binary(store=True, index=True)
    base_no = fields.Char(store=True)
    base_account_no = fields.Char(store=True)
    pick_location_id = fields.Many2one('pickup.location', store=True)
    card_type = fields.Many2one('type.card', 'Card Type')
    prepayment_percentage = fields.Selection([('3','3%'),('10','10%'),('other','other%')])
    percent = fields.Float()

    _sql_constraints = [
        ('unique_base_no', "unique(base_no)", " Base Number must be unique."),
        ('unique_base_account_no', "unique(base_account_no)", "Account Number must be unique."),
    ]

    def get_personal_data(self):
        if self.partner_id:
            contact = self.env['crm.lead'].search([('client_id','=',self.partner_id.id)])
            self.service_type_id = self.env['service.type'].search([('serial_no','=',1)],limit=1).id
            self.account_no = contact.account_no
            self.base_no = contact.account_no
            self.applicant_name = contact.applicant_name
            self.nationality = contact.nationality.id
            self.employer_id = contact.employer_id.id
            self.passport_no = contact.passport_no
            self.passport_expiry = contact.passport_expiry
            self.birthday = contact.birthday
            self.age = contact.age
            self.degree_level = contact.degree_level
            self.martial_status = contact.martial_status
            self.no_of_dependent = contact.no_of_dependent
            self.email_con = contact.email_con
            self.mobile_con = contact.mobile_con
            self.street_home = contact.street_home
            self.street2_home = contact.street2_home
            self.street_work = contact.street_work
            self.street2_work = contact.street2_work
            self.state_id_home = contact.state_id_home.id
            self.state_id_work = contact.state_id_work.id
            self.city_home = contact.city_home
            self.city_work = contact.city_work
            self.country_id_home = contact.country_id_home.id
            self.country_id_work = contact.country_id_work.id
            self.zip_home = contact.zip_home
            self.zip_work = contact.zip_work
            self.flat_no_work = contact.flat_no_work
            self.flat_no_home = contact.flat_no_home
            self.building_home = contact.building_home
            self.building_work = contact.building_work
            self.monthly_salary = contact.monthly_salary
            self.monthly_income = contact.monthly_income
            self.other_income = contact.other_income
            self.is_blacklisted = contact.is_blacklisted
            self.passport_attachment = contact.passport_attachment
            self.fatch_form_attachment = contact.fatch_form_attachment
            self.dcard_number = contact.dcard_number
            self.arrival_time = contact.arrival_time
            self.airline_agency = contact.airline_agency
            self.flight_reference = contact.flight_reference
            self.departure_city = contact.departure_city
            self.arrival_city = contact.arrival_city
            self.sales_agent = contact.sales_agent.id
            self.sales_agent_id = contact.sales_agent_id
            self.sales_officer = contact.sales_officer.id
            self.sales_department = contact.sales_department.id
            self.sales_deadline = contact.sales_deadline
            self.digital_signature_attach = contact.digital_signature_attach
            self.account_op_form = contact.account_op_form
            self.dcard_form = contact.dcard_form
            self.undertaking_form = contact.undertaking_form

    def button_reviewed(self):
        return self.write({'state':'reviewed'})

    def button_returned(self):
        return self.write({'state':'returned'})

    def button_cpv_failed(self):
        return self.write({'state':'cpv_failed'})

    def button_cpv_pending(self):
        return self.write({'state':'cpv_pending'})

    def button_submit(self):
        return self.write({'state':'submitted'})

    def button_send_production(self):
        return self.write({'state':'sent_for_prod'})

    def button_delivered(self):
        return self.write({'state': 'delivered'})

    def button_approved(self):
        self.action_confirm()

    def button_proceed_production(self):
        users = self.env.ref('crm_customization.group_production_responsible').users
        for user in users:
            self.action_send_prod_email(user.email)

    def action_send_prod_email(self,email_to):
        template_id = self.env.ref('crm_customization.email_template_operation_send').id
        template = self.env['mail.template'].browse(template_id)
        template.write({'email_to': email_to})
        template.send_mail(self.id,force_send=True)

    @api.depends('birthday')
    def get_age(self):
        res = {}
        for rec in self:
            if rec.birthday:
                birthday = rec.birthday
                age_calc = (datetime.date.today() - birthday).days / 365
                age = str(age_calc)
                rec.age = age


class OperationReq(models.Model):
    _name = 'operation.request'
    name = fields.Char()


class LocationPick(models.Model):
    _name = 'pickup.location'

    name = fields.Char('Street Address')
    city = fields.Char('City')
    country_id = fields.Many2one('res.country', 'Country')


class ServiceType(models.Model):
    _name = 'service.type'

    serial_no = fields.Integer('Serial', required=True)
    name = fields.Char('Service Name', required=True)

    _sql_constraints = [
        ('unique_serial_no', "unique(serial_no)", "Serial must be unique.")]


class CardType(models.Model):
    _name = 'type.card'

    serial_no = fields.Integer('Serial', required=True)
    name = fields.Char('Name', required=True)

    _sql_constraints = [
        ('unique_serial_no', "unique(serial_no)", "Serial must be unique.")]


class StatusArrival(models.Model):
    _name = 'arrival.status'
    _description = 'Arrival Status'

    name = fields.Char('Name', required=True, store=True)








