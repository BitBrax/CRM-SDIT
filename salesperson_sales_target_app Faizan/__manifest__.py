# -*- coding: utf-8 -*-

{
    'name': 'Sales Target Based Sales Person',
    'author': 'Edge Technologies',
    'version': '14.0.1.1',
    'live_test_url':'https://youtu.be/ksExOXqA2bg',
    "images":['static/description/main_screenshot.png'],
    'summary': 'Total Sales Target for Sales Person Target for salesperson target sales order target sales goal sales person goal sales team target sales person wise target for sales order target based on salesman target for sales target based on salesman goal for sales',
    'description': """ Sales Person Sales Target """,
    "license" : "OPL-1",
    'depends': ['base','sale_management','purchase','stock','hr','resource'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/mail_template.xml',
        'views/sale_target.xml',
        'views/sale_target_line.xml',
        'views/sale_target_batch.xml',
    ],
    'qweb' : [],
    'demo': [],
    'css': [],
    'installable': True,
    'auto_install': False,
    'price':32,
    'currency': "EUR",
    'category': 'Sales',
}
