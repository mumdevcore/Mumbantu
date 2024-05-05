# -*- coding: utf-8 -*-
{
    'name': "Key Performance Indicator MUM",

    'summary': """
        Key Performance Indicator MUM
            - KPI Karyawan
            - KPI Bagian
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "PT Mitra Utama Madani",
    'website': "https://www.mum.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mum_backend_customization', 'hr',],

    # always loaded
    'data': [
        'data/sequence.xml',
        'data/res_month_data.xml',
        'security/group.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',

        'views/employee_kro_kpi.xml',
        'views/employee_ro_kpi.xml',
        'views/employee_alw_kpi.xml',
        'views/employee_kpi_portofolio.xml',
        'views/kpi_manajemen_batch.xml',
        'views/manajemen_kpi_bagian.xml',
        'views/manajemen_kpi_bagian_line.xml',
        'views/master.xml',
        'views/hr_job.xml',
        'views/grading.xml',
        'views/kpi_mekaar_batch.xml',
        'views/res_config_settings.xml',
        'views/menu_item.xml',
        
    ],
}
