{
    'name': 'Odoo Untouched CRM Opportunities',
    'version': '12.0',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://pragtech.co.in',
    'category': 'CRM',
    'summary': 'Odoo Untouched CRM Opportunities Pragtech Opportunity Activity Notification CRM opportunities odoo opportunites Untouched Opportunities',
    'description': """ 
Add new notification on mail activity Lead/Opportunity as untouch 
<keywords>
Pragtech Opportunity Activity Notification
CRM opportunities
odoo opportunites
Untouched Opportunities
       """,
    'depends': ['crm', 'mail'],
    'data': [
        'views/res_config_setting_view.xml',
        'views/crm_search_view.xml',
        'views/assets.xml'
    ],
    'qweb': ['static/src/xml/systray.xml'],
    'images': ['static/description/Animated-untouched-activity.gif'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=310&name=support-odoo-untouched-crm-opportunities',
    'license': 'OPL-1',
    'price': 29,
    'currency': 'EUR',
    'license': 'OPL-1',
    "active": False,
    "installable": True,
}
