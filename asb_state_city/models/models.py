# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Country(models.Model):
    _inherit = "res.country"
    
    state_ids = fields.One2many('res.country.state','country_id',"Propinsi")
    
class State(models.Model):
    _inherit = "res.country.state"
    
    code = fields.Char(size=255)
    city_ids = fields.One2many("res.state.city","state_id", "Kota/Kabupaten")
    # active = fields.Boolean('Active', default=False)
    
    # @api.onchange('active')
    # def update_state_active(self):
    #     self._cr.execute("""UPDATE res_country_state SET active = FALSE""")

class City(models.Model):
    _name = "res.city"
    _description = 'Kota/Kabupaten'
    
    name = fields.Char("Nama Kota/Kabupaten")
    kabupaten = fields.Boolean('Kabupaten')
    code = fields.Char("Kode Kota")
    state_id = fields.Many2one('res.country.state', 'Propinsi', index=True)
    kecamatan_ids = fields.One2many('res.city.kecamatan', 'city_id','Kecamatan')

class Kecamatan(models.Model):
    _name = 'res.kecamatan'
    _description = 'Kecamatan'
    
    name = fields.Char('Nama Kecamatan')
    code = fields.Char('Kode Kecamatan')
    city_id = fields.Many2one('res.state.city', 'Kota/Kabupaten', index=True)
    kelurahan_ids = fields.One2many('res.kecamatan.kelurahan', 'kecamatan_id','Kelurahan')
    
    
class Kelurahan(models.Model):
    _name = 'res.kecamatan.kelurahan'
    _description = 'Kelurahan'
    
    name = fields.Char('Nama Kelurahan/Desa')
    zip = fields.Char('Kodepos')
    desa = fields.Boolean('Desa')
    kecamatan_id = fields.Many2one('res.city.kecamatan','Kecamatan', index=True)

