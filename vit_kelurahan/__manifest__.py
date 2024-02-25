{
	"name": "Data Kelurahan, Kecamatan, Propinsi Indonesia",
	"version": "1.2",
	"depends": [
		"base",
		"sale"
	],
	"author": "vitraining.com",
	"category": "Sales",
	'website': 'http://www.vitraining.com',
	"description": """\

this module provide kecamatan, kelurahan, and state data for indonesian


            Find our other interesting modules that can make your life easier:
            https://www.odoo.com/apps/modules/browse?search=vitraining
""",
	'depends': ['base', 'contacts'],
	"data": [
		# "data/res.country.state.csv",
		# "data/vit.kota.csv",
		# "data/vit.kecamatan.csv",
		# "data/vit.kelurahan.csv",
		"security/group.xml",
		"security/ir.model.access.csv",
		"view/kelurahan.xml",
		"view/kecamatan.xml",
		"view/kota.xml",
		"view/partner.xml",
	],
	"installable": True,
	"auto_install": False,
    "application": True,
}