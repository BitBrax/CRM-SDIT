# -*- coding: utf-8 -*-

{
    'name': 'Sales Eligibility Criteria',
    'author': 'SIT & Think Digital',
    'version': '14.0.1.1',
    'summary': 'Total Sales Target for Sales Person Target for salesperson target sales order target sales goal sales person goal sales team target sales person wise target for sales order target based on salesman target for sales target based on salesman goal for sales',
    'description': """ Sales Eligibility Criteria """,
    "license" : "OPL-1",
    'depends': ['base','sale_management','purchase','stock','hr','product','salesperson_sales_target_app'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/sale_criteria.xml'
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
