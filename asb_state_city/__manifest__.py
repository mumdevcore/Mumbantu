# -*- coding: utf-8 -*-
{
    'name': 'City',
    'version': '0.1',
    'author': 'PT Arkana Solusi Bisnis',
    'license': 'OPL-1',
    'category': 'Master',
    'website': 'http://www.arkana.co.id/',
    'summary': 'City Kecamatan Kelurahan (Indonesia)',
    'description': '''
        City Kecamatan Kelurahan (Indonesia)
    ''',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/city_view.xml',
        'views/res_view.xml',
        # 'views/branch_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}