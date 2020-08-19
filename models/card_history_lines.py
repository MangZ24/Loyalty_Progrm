from odoo import api, fields, models


class CardHistoryLines(models.Model):
    _name = 'card.history.lines'
    _description = 'Card History'

    card_id = fields.Many2one(comodel_name="card.card", string="Card IDs", required=False, )
    card_number = fields.Char(related="card_id.card_number", string="Loyalty #", store=True)
    sale_order = fields.Char(string="Sale Order #",)
    point_recieved = fields.Float(string="Point received", default=0.0)
    point_used = fields.Float(string="Point used", default=0.0)
    date_paid = fields.Datetime(string="Date Paid")