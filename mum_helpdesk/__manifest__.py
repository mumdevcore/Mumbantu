# -*- coding: utf-8 -*-
{
    'name': "Helpdesk MUM",

    'summary': """
        Helpdesk PT Mitra Utama Madani""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Agus Priyanto",
    'website': "https://hci.mum.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk_mgmt', 'report_xlsx'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/ir_rule.xml',


        'views/stage.xml',
        'views/ticket.xml',
        'views/category.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
