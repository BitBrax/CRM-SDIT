# -*- coding: utf-8 -*-

{
    'name': "Lead Flow",
    'summary': """Lead flow customizations""",
    'description': """ Module for the sale lead flow customizations .""",
    'author': "SIT & Think Digital",
    'website': "",
    'category': 'Sale',
    'version': '0.1',
    'depends': ['base','mail','sales_eligibility'],
    'data': ['security/ir.model.access.csv',
             'data/data.xml',
             'data/cron_view.xml',
             'views/views.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
