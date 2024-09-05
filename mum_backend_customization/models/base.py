# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _
from num2words import num2words
import pytz
from odoo.tools.float_utils import float_round
from datetime import datetime, time
# from datetime import datetime
ID_MONTHES = {
			'01': {
				'B' : 'Januari',
				'b' : 'Jan',
			},
			'02': {
				'B' : 'Februari',
				'b' : 'Feb',
			},
			'03': {
				'B' : 'Maret',
				'b' : 'Mar',
			},
			'04': {
				'B' : 'April',
				'b' : 'Apr',
			},
			'05': {
				'B' : 'Mei',
				'b' : 'Mei',
			},
			'06': {
				'B' : 'Juni',
				'b' : 'Jun',
			},
			'07': {
				'B' : 'Juli',
				'b' : 'Jul',
			},
			'08': {
				'B' : 'Agustus',
				'b' : 'Agt',
			},
			'09': {
				'B' : 'September',
				'b' : 'Sep',
			},
			'10': {
				'B' : 'Oktober',
				'b' : 'Okt',
			},
			'11': {
				'B' : 'Nopember',
				'b' : 'Nop',
			},
			'12': {
				'B' : 'Desember',
				'b' : 'Des',
			},
	}

def datetime_to_id_strftime(timestamp, month_key):
	tgl = timestamp.strftime("%d")
	bln = ID_MONTHES[timestamp.strftime("%m")][month_key]
	thn = timestamp.strftime("%Y")
	return ' '.join(x for x in [tgl,bln,thn])


class BaseModel(models.AbstractModel):
	_inherit = 'base'

	# rev_status = fields.Char(string='Revision Status',)


	def _convert_to_id_month(self, timestamp, month_key):
		if not timestamp:
			return
		return datetime_to_id_strftime(timestamp, month_key)

	def num2words(self, amount, lang, currency_id):
		if not currency_id:
			currency_id = self.env.company.currency_id
		valueR = float_round(amount, precision_digits=0)
		value = int(valueR) if valueR % 1 == 0 else (valueR)
		return f"{num2words(value, lang=lang)} {currency_id.currency_unit_label}".title()

	def _get_approver(self):
		res_id = f"{self._name},{self.id}"
		approval_line = self.env['multi.approval'].search([('origin_ref', '=', res_id)]).line_ids
		return approval_line
	
	def _get_id_monthes(self, timestamp, month_key):
		month = timestamp.strftime('%m')
		return ID_MONTHES[month][month_key]

	def float_to_datetime(self, date, float_time, tz):
		utc = pytz.timezone('UTC')
		conversion = '{0:02.0f}:{1:02.0f}'.format(*divmod(float_time * 60, 60))
		hour, minute = conversion.split(":")
		conversion_datetime = tz.localize(datetime.combine(date, time(int(hour), int(minute)))).astimezone(utc).replace(tzinfo=None)
		return conversion_datetime

	def local_timezone_to_utc(self, timestamp, tz):
		utc = pytz.utc
		local_tz = pytz.timezone(tz)
		return local_tz.localize(timestamp).astimezone(utc).replace(tzinfo=None)