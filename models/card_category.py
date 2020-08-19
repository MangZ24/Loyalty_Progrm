from odoo import api, fields, models
from odoo.tools.translate import _


class CardCategory(models.Model):
    _name = 'card.category'
    _description = 'Loyalty Card Category'

    name = fields.Char(string='Name', required=True)
    is_active = fields.Boolean(string='Is Active?')
    type_ids = fields.One2many(string='Types', comodel_name='card.type', inverse_name='categ_id')

    _sql_constraints = [
        ('uniq_name', "unique(name)",
         _('Name value has been existed. Please choose another !'))]