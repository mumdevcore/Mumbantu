# -*- coding: utf-8 -*-
from odoo import models,fields,api

class ResCompany(models.Model):
    _inherit = "res.company"
    
    city_id = fields.Many2one('res.state.city', 'Kabupaten')
    kecamatan_id = fields.Many2one('res.city.kecamatan', 'Kecamatan', domain=[('city_id', '=', 'city_id')])
    kelurahan_id = fields.Many2one('res.kecamatan.kelurahan', 'Kelurahan', domain="[('kecamatan_id','=',kecamatan_id)]")

# class ClientBranch(models.Model):
#     _inherit = 'client.branch'
    
#     state_id = fields.Many2one('res.country.state', "State", domain="[('country_id','=',country_id)]")
#     city_id = fields.Many2one('res.state.city', 'Kabupaten', domain="[('state_id','=',state_id)]")
#     kecamatan_id = fields.Many2one('res.city.kecamatan', 'Kecamatan', domain=[('city_id', '=', 'city_id')])
#     kelurahan_id = fields.Many2one('res.kecamatan.kelurahan', 'Kelurahan', domain="[('kecamatan_id','=',kecamatan_id)]")
    

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    state_id = fields.Many2one('res.country.state', "State", domain="[('country_id','=',country_id)]")
    city_id = fields.Many2one('res.state.city', 'Kabupaten', domain="[('state_id','=',state_id)]")
    kecamatan_id = fields.Many2one('res.city.kecamatan', 'Kecamatan', domain=[('city_id', '=', 'city_id')])
    kelurahan_id = fields.Many2one('res.kecamatan.kelurahan', 'Kelurahan', domain="[('kecamatan_id','=',kecamatan_id)]")

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False
            self.city_id = False
            self.kecamatan_id = False
            self.kelurahan_id = False

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id and self.city_id != self.city_id.state_id:
            self.city_id = False
            self.kecamatan_id = False
            self.kelurahan_id = False

    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id and self.kecamatan_id != self.kecamatan_id.city_id:
            self.kecamatan_id = False
            self.kelurahan_id = False
    
    @api.onchange('kecamatan_id')
    def _onchange_kecamatan_id(self):
        if self.kecamatan_id and self.kelurahan_id != self.kelurahan_id.kecamatan_id:
            self.kelurahan_id = False
    
    def init(self):
        self._cr.execute('select id from %s limit 1;' %self.env['res.kecamatan.kelurahan']._table)
        if self._cr.fetchall():
            return
        self._uninstall_hook(self._cr)
        self._post_init_hook(self._cr)
    
    def _post_init_hook(self, cr):
        import os, csv
        from odoo.api import Environment, SUPERUSER_ID
        
        env = Environment(cr, SUPERUSER_ID, {})
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # country = env['res.country'].search([])
        # country_ids = {}
        # for country_id in country:
        #     country_metadata = country_id.get_metadata()[0]
        #     country_ids.update({country_metadata['xmlid']: country_metadata['id']}) 

        # with open(dir_path + '/res.country.state.csv', 'rt') as csvfile:
        #     state_values = []
        #     for row in csv.DictReader(csvfile, delimiter=','):
        #         state_values.append(cr.mogrify('(%s, %s, %s, %s)', (
        #             country_ids[row['country_id:code']],
        #             row['code'],
        #             row['name'],
        #             row['active'].upper() == 'TRUE')).decode())
        #     cr.execute("""
        #     WITH insert_data AS (
        #         INSERT INTO res_country_state (country_id, code, name, active) VALUES %s RETURNING id)
        #     INSERT INTO ir_model_data (module, name, model, res_id) SELECT 'country_state', id, 'res.country.state', id FROM insert_data RETURNING name, res_id
        #     """ % ','.join(state_values))
        #     state_ids = dict(cr.fetchall())
        
        indonesia_id = env.ref('base.id')
        states = env['res.country.state'].search([('country_id','=', indonesia_id.id)])
        state_ids = {}
        for state in states:
            state_metadata = state.get_metadata()[0]
            state_ids.update({state_metadata['xmlid']: state_metadata['id']}) 
        
        with open(dir_path + '/res.state.city.csv', 'rt') as csvfile:
            city_values = []
            for row in csv.DictReader(csvfile, delimiter=',', quotechar='"'):
                city_values.append(cr.mogrify('(%s, %s, %s, %s)', (
                    state_ids[row['state_id/id']],
                    row['code'],
                    row['name'],
                    row['kabupaten'].upper() == 'TRUE')).decode())
            cr.execute("""
            WITH insert_data AS (
                INSERT INTO res_state_city (state_id, code, name, kabupaten) VALUES %s RETURNING code, id)
            INSERT INTO ir_model_data (module, name, model, res_id) SELECT 'state_city', code, 'res.state.city', id FROM insert_data RETURNING name, res_id
            """ % ','.join(city_values))
            city_ids = dict(cr.fetchall())
        
        with open(dir_path + '/res.city.kecamatan.csv', 'rt') as csvfile:
            kecamatan_values = []
            for row in csv.DictReader(csvfile, delimiter=',', quotechar='"'):
                kecamatan_values.append(cr.mogrify('(%s, %s, %s)', (
                    city_ids[row['city_id/id'].replace('asb_state_city.', '')],
                    row['code'],
                    row['name'])).decode())
            cr.execute("""
            WITH insert_data AS (
                INSERT INTO res_city_kecamatan (city_id, code, name) VALUES %s RETURNING code, id)
            INSERT INTO ir_model_data (module, name, model, res_id) SELECT 'state_city', code, 'res.city.kecamatan', id FROM insert_data RETURNING name, res_id
            """ % ','.join(kecamatan_values))
            kecamatan_ids = dict(cr.fetchall())
            
        with open(dir_path + '/res.kecamatan.kelurahan.csv', 'rt') as csvfile:
            kelurahan_values = []
            for row in csv.DictReader(csvfile, delimiter=',', quotechar='"'):
                kelurahan_values.append(cr.mogrify('(%s, %s, %s, %s)', (
                    kecamatan_ids[row['kecamatan_id/id'].replace('asb_state_city.', '')],
                    row['zip'],
                    row['name'],
                    row['desa'].upper() == 'TRUE')).decode())
            cr.execute("""
            WITH insert_data AS (
                INSERT INTO res_kecamatan_kelurahan (kecamatan_id, zip, name, desa) VALUES %s RETURNING id)
            INSERT INTO ir_model_data (module, name, model, res_id) SELECT 'state_city', CONCAt('res_kecamatan_kelurahan_',id::TEXT), 'res.kecamatan.kelurahan', id FROM insert_data
                
            """ % ','.join(kelurahan_values))
        cr.commit()

    def _uninstall_hook(self, cr):
        cr.execute("""
            DELETE FROM res_country_state WHERE id IN (
                SELECT res_id FROM ir_model_data WHERE model = 'res.country.state' AND module = 'state_city');
            DELETE FROM ir_model_data WHERE model = 'res.country.state' AND module = 'state_city';
            
            DELETE FROM res_state_city WHERE id IN (
                SELECT res_id FROM ir_model_data WHERE model = 'res.state.city' AND module = 'state_city');
            DELETE FROM ir_model_data WHERE model = 'res.state.city' AND module = 'state_city';
            
            DELETE FROM res_city_kecamatan WHERE id IN (
                SELECT res_id FROM ir_model_data WHERE model = 'res.city.kecamatan' AND module = 'state_city');
            DELETE FROM ir_model_data WHERE model = 'res.city.kecamatan' AND module = 'state_city';
            
            DELETE FROM res_kecamatan_kelurahan WHERE id IN (
                SELECT res_id FROM ir_model_data WHERE model = 'res.kecamatan.kelurahan' AND module = 'state_city');
            DELETE FROM ir_model_data WHERE model = 'res.kecamatan.kelurahan' AND module = 'state_city';
        """)