# -*- coding: utf-8 -*-
{
    'name': "MUM Report ",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PT Mitra Utama Madani",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'report_xlsx',
        'mum_kpi',
        'mum_backend_customization',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/action.xml',
        # 'views/templates.xml',
    ]
}
