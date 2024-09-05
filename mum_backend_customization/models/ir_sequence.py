# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta
import logging
import pytz
from odoo.exceptions import UserError

from collections import OrderedDict

from odoo import fields, models, api, _
import re
special_char = r'\W+'
_logger = logging.getLogger(__name__)
ID_MONTHES = {
			'01': 'Januari ',
			'02': 'Februari ',
			'03': 'Maret ',
			'04': 'April ',
			'05': 'Mei ',
			'06': 'Juni ',
			'07': 'Juli ',
			'08': 'Agustus ',
			'09': 'September ',
			'10': 'Oktober ',
			'11': 'Nopember ',
			'12': 'Desember ',
	}


class IrSequence(models.Model):
	_inherit = 'ir.sequence'

	def write_roman(self,num):

		roman = OrderedDict()
		roman[1000] = "M"
		roman[900] = "CM"
		roman[500] = "D"
		roman[400] = "CD"
		roman[100] = "C"
		roman[90] = "XC"
		roman[50] = "L"
		roman[40] = "XL"
		roman[10] = "X"
		roman[9] = "IX"
		roman[5] = "V"
		roman[4] = "IV"
		roman[1] = "I"

		def roman_num(num):
			for r in roman.keys():
				x, y = divmod(num, r)
				yield roman[r] * x
				num -= (r * x)
				if num > 0:
					roman_num(num)
				else:
					break

		return "".join([a for a in roman_num(num)])

	def _get_prefix_suffix(self, date=None, date_range=None):
		def _interpolate(s, d):
			return (s % d) if s else ''

		def _interpolation_dict():
			now = range_date = effective_date = datetime.now(pytz.timezone(self._context.get('tz') or 'UTC'))
			if date or self._context.get('ir_sequence_date'):
				effective_date = fields.Datetime.from_string(date or self._context.get('ir_sequence_date'))
			if date_range or self._context.get('ir_sequence_date_range'):
				range_date = fields.Datetime.from_string(date_range or self._context.get('ir_sequence_date_range'))

			sequences = {
				'year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
				'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S', 'rom_year': '%Y', 
				'rom_month': '%m', 'rom_y': '%y', 'rom_day': '%d'}
			res = {}
			for key, format in sequences.items():
				if "rom_" in key:
					res[key] = self.write_roman(int(effective_date.strftime(format)))
					res['range_' + key] = self.write_roman(int(range_date.strftime(format)))
					res['current_' + key] = self.write_roman(int(now.strftime(format)))
				else:
					res[key] = effective_date.strftime(format)
					res['range_' + key] = range_date.strftime(format)
					res['current_' + key] = now.strftime(format)
			return res

		self.ensure_one()
		d = _interpolation_dict()
		try:
			interpolated_prefix = _interpolate(self.prefix, d)
			interpolated_suffix = _interpolate(self.suffix, d)
		except ValueError:
			raise UserError(_('Invalid prefix or suffix for sequence \'%s\'') % self.name)
		return interpolated_prefix, interpolated_suffix

	def find_missing_sequence(self, number_list=None, sequence_date=None, sequence_ref=None):
		if not number_list:
			return
		if not sequence_ref:
			return

		# current_sequence = self._get_current_sequence(sequence_date=sequence_date)
		ref = sequence_ref.split(',')
		current_sequence = self.env[ref[0]].browse(ref[1])
		def split_sequence(seq):
			split_sequence = re.split(special_char, seq)
			no = self.prefix and split_sequence[-1] or split_sequence[0]
			return int(no)
		no = sorted([split_sequence(no) for no in number_list])
		sequence_gap = no and list(set(range(1, no[-1] + 1)) - set(no)) or []

		# if sequence_gap
		current_sequence.number_next = sequence_gap and min(sequence_gap) or current_sequence.number_next
		return current_sequence

		# - buat text utk resource sequence dan id cetak dengan format 'object,id' cth.  'ir.sequence,1'
		# - pada method create sebelum super, cari semua nomor sequence yg memiliki resource yang sama dan mapping nomor sequence nya
		# - jalankan method find_missing_sequence(number, sequence_date)  berikan tanggal pada field parameter sequence_date