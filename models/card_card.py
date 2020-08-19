from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import Warning
from dateutil.relativedelta import relativedelta


class CardCard(models.Model):
    _name = 'card.card'
    _rec_name = 'card_number'
    _description = 'Loyalty Card'

    card_number = fields.Char(string='Loyalty #', required=True, readonly=True, copy=False, index=True,
                              default=lambda self: _('New'), store=True,)
    partner_id = fields.Many2one(string='Customer', comodel_name='res.partner', )

    type_id = fields.Many2one(string='Type', comodel_name='card.type', required=True, )
    barcode = fields.Char(string="Barcode", store=True,)
    total_point = fields.Float(string="Accumulated Points", readonly=True, store=False, compute="_get_points")
    is_active = fields.Boolean(string="is Active?", )
    is_expired = fields.Boolean(string="is Expired?", )
    expected_date = fields.Date(string="Expected Date\n(Release Card Date)",)
    expiration_date = fields.Date(string="Expiration Date", readonly=True,)
    activation_date = fields.Date(string="Activation Date", readonly=True,)

    created_date = fields.Date(string='Created Date', default=fields.Date.today())
    updated_date = fields.Date(string="Updated Date", )

    history_ids = fields.One2many(string="History", comodel_name="card.history.lines", inverse_name="card_id", )
    account_invoice_lines = fields.One2many(string="Invoices", comodel_name="account.invoice", inverse_name="card_ids",
                                            )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_use', 'In Use'),
        ('canceled', 'Canceled'),
        ('locked', 'Locked'),
    ], string='Status', readonly=True, default='draft', )


    @api.depends('type_id')
    def _get_points(self):
        accumulated_points = []
        points_used = []
        for rec in self:
            basic_points = rec.type_id.basic_point
            # print basic_points
            if rec.account_invoice_lines:
                for data in rec.account_invoice_lines:
                    points_used.append(data.points_used)
                    if data.state == 'paid':
                        accumulated_points.append(data.points_received)
                    points = sum(accumulated_points) - sum(points_used)
                    rec.total_point = basic_points + points
            else:
                rec.total_point = basic_points

    @api.model
    def create(self, vals):
        if vals.get('card_number', _('New')) == _('New'):
            vals['card_number'] = self.env['ir.sequence'].next_by_code('card.number.sequence')
            result = super(CardCard, self).create(vals)
            return result

    @api.multi
    def btn_confirm(self):
        for rec in self:
            partner_id = self.env['card.card'].search([('partner_id', '=', rec.partner_id.id),
                                                       ('state', '!=', 'draft')], limit=1)
            if not rec.partner_id:
                raise Warning(_('''
                            Error! Empty customer!
                            '''))
            elif partner_id:
                raise Warning(_('''
                            Error! Customer "{}" was already registered on loyalty card.
                            '''.format(rec.partner_id.name)))
                return False

            rec.write({'state': 'confirmed'})


    @api.multi
    def btn_activate(self):
        for rec in self:

            nb = rec.type_id.period_id.nb
            period = rec.type_id.period_id.period

            if period == 'month':
                expiry_date = date.today() + relativedelta(months=nb)
                expiration_date = expiry_date
            else:
                expiry_date = date.today() + relativedelta(years=nb)
                expiration_date = expiry_date

            rec.write({'state': 'in_use', 'expiration_date': expiration_date, 'activation_date': date.today()})

    @api.multi
    def btn_cancel(self):
        for rec in self:
            rec.write({'state': 'canceled'})

    @api.multi
    def btn_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    @api.multi
    def btn_lock(self):
        for rec in self:
            rec.write({'state': 'locked'})

class GenerateCards(models.TransientModel):
    _name = 'generate.cards'
    _description = 'Generate Cards'

    qty = fields.Integer(string='Quantity', required=True )
    type_id = fields.Many2one(string='Type', comodel_name='card.type', required=1)

    @api.multi
    def button_create(self):
        self.ensure_one()
        cards = Card = self.env['card.card']
        if self.qty > 0:
            for _ in range(self.qty):
                vals = {
                    'type_id': self.type_id.id
                }
                cards |= Card.create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'card.card',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {},
            'domain': [('id', 'in', cards.ids)],
        }
        return True




