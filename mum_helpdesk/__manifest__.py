# -*- coding: utf-8 -*-
{
    'name': "Helpdesk MUM",

    'summary': """
        Helpdesk PT Mitra Utama Madani""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Agus Priyanto",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk_mgmt', 'mum_backend_customization'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/ticket.xml',
        'views/category.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
