from datetime import datetime, date, timedelta
import calendar
from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

PERIOD = [('month', 'Month(s)'), ('year', 'Year(s)')]

class CardPeriod(models.Model):
    _name = 'card.period'
    _description = 'Loyalty Card Period'

    name = fields.Char(
        string='Period',
        compute='_get_period_name',
        store=1)
    nb = fields.Integer(
        string='Number of Months / Years',
        required=True)
    period = fields.Selection(
        PERIOD,
        string='Period',
        required=True)

    @api.multi
    @api.depends('nb', 'period')
    def _get_period_name(self):
        period = dict(PERIOD)
        for record in self:
            record.name = '{} {}'.format(record.nb, period.get(record.period))

    @api.multi
    def get_period_end_date(self, start_d=None):
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = int(sourcedate.year + month / 12 )
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return date(year, month, day)

        self.ensure_one()
        if not start_d:
            start_d = fields.Date.context_today(self)
        start_d = datetime.strptime(start_d, DF)
        mon = self.nb
        if self.period == 'year':
            mon *= 12
        end_date = add_months(start_d, mon)
        return end_date

    def _create(self, vals):
        if vals.get('nb') == 0 :
            raise Warning(_('''
                            Error! Please don't leave highlighted field zero (0.00).
                            * Number of Months / Years
                        '''))
            return False
        else:
            result = super(CardPeriod, self)._create(vals)
            return result

    _sql_constraints = [
        ('uniq_name', "unique(name)",
         _('This period has been existed. Please pick another period!'))]
