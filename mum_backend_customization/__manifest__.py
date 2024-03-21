# -*- coding: utf-8 -*-
{
    'name': "MUM Backend Customization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PT Mitra Utama Madani",
    'website': "https://www.mum.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        'sequence_reset_period',
        'calendar',
        'contacts',
        'vit_kelurahan',
        'hr', 
        # 'hr_skills'
        ],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        # 'data/res_month_data.xml',

        'wizards/calendar_add_member_wizard.xml',
        'wizards/training_employee_suggestion_wizard.xml',

        
        'views/hr_job.xml',
        'views/master_data.xml',
        'views/hr_certification.xml',
        'views/training_needs_analysis.xml',
        'views/hr_employee.xml',
        'views/hr_employee_public.xml',
        'views/calendar.xml',
        # 'views/employee_kpi.xml',
        # 'views/grading_master_template.xml',
        # 'views/grading.xml',

        'views/menu_item.xml',
    ],
}
