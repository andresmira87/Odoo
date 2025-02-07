# -*- coding: utf-8 -*-
{
    'name': "votaciones",

    'summary': "Sistema de votaciones para universidad UNIACME",

    'description': """
Long description of module's purpose
    """,

    'author': "Andres Felipe Mira Pineda",
    'website': "https://www.linkedin.com/in/andres-felipe-mira-pineda-baa525239/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Education',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

