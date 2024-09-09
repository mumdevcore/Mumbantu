# -*- coding: utf-8 -*-
{
    'name': "MUM Budget",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
            'base', 
            'account',
            'mum_backend_customization',
            'om_account_budget',
            'hr_expense',
            ],

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/group.xml',
        'security/ir.model.access.csv',

        # 'reports/expense_report.xml',
        'reports/memo_pembayaran_detail.xml',
        'reports/memo_pembayaran.xml',
        'reports/form_ceklist_permintaan_pembayaran_pdf.xml',

        'views/views.xml',
        # 'views/budget_tahunan.xml',
        'views/anggaran_divisi.xml',
        'views/anggaran_bulanan_divisi.xml',
        'views/pengajuan_anggaran.xml',
        'views/account_budget_parent.xml',
        'views/hr_expense.xml',
        'views/crossovered_budget.xml',
        'views/program_kerja.xml',
        'views/spd.xml',
        'views/job_title.xml',
        'views/account_move.xml',
        'views/memo_pembayaran.xml',
        'views/res_config_settings.xml',
        'views/template_lampiran_invoice.xml',

        'views/menu_item.xml',
    ]
}
