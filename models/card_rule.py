from odoo import api, fields, models, _
from odoo.exceptions import Warning

class CardRule(models.Model):
    _name = 'card.rule'
    _description = 'Card Rule'

    name = fields.Char(string="Name", required=True)
    min_purchase_amount = fields.Float(string="Min. Purchase Amount", required=True,)
    points = fields.Float(string="Point/s", required=True,)
    is_active = fields.Boolean(string="Is Active?")
    note = fields.Text(string='Note')

    def _create(self, vals):
        if vals.get('points') == 0.00 and vals.get('min_purchase_amount') == 0.00:
            raise Warning(_('''
                            Error! Please don't leave highlighted field zero (0.00).
                            * Point/s
                            * Minimum Purchase Amount
                        '''))
            return False
        elif vals.get('points') == 0.00:
            raise Warning(_('''
                            Error! Please don't leave highlighted field zero (0.00).
                            * Point/s
                        '''))
            return False
        elif vals.get('min_purchase_amount') == 0.00:
            raise Warning(_('''
                            Error! Please don't leave highlighted field zero (0.00).
                            * Minimum Purchase Amount
                        '''))
            return False
        else:
            result = super(CardRule, self)._create(vals)
            return result

    _sql_constraints = [
        ('uniq_name', "unique(name)",
         _('Rule name has been existed. Please change another !'))]
