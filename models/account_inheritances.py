from addons.account.models.account_payment import  MAP_INVOICE_TYPE_PARTNER_TYPE
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'
    _description = 'Account Invoice Inherit'

    card_ids = fields.Many2one(string="Loyalty #", comodel_name="card.card", search="_search_by_card", store=True,)
    card_number = fields.Char(string="Loyalty Card #", store=True)
    points_received = fields.Float(string="Points Received", default=0.0,
                                   compute="_get_points"
                                   )
    available_point = fields.Float(string="Available Points", default=0.0, compute="_get_available_points")
    points_used = fields.Float(string="Redeem Points", default=0.0, )
    discounted_amount = fields.Float(string="Discounted Amount", default=0.0, compute="_discounted_amount")

    @api.multi
    def _dump_func(self):
        pass

    @api.multi
    def _search_by_card(self, operator, value):
        partner_ids = []
        if value:
            args = [('partner_id', '!=', False)]
            cards = self.env['card.card'].name_search(value, args)
            if cards:
                card_ids = [x[0] for x in cards]
                cards = self.env['card.card'].browse(card_ids)
                partner_ids = [x.partner_id.id for x in cards]
        return [('partner_id', 'in', partner_ids)]

    @api.onchange('card_ids')
    def _set_customer(self):
        for order in self:
            if not self.card_ids or not self.card_ids.partner_id:
                continue
            order.partner_id = self.card_ids.partner_id

    @api.multi
    @api.depends('card_ids')
    def _get_available_points(self):
        available_point = []
        points_used = []
        # print self.card_ids.id
        basic_points = self.card_ids.type_id.basic_point
        for data in self:
            account_invoice_lines = super(AccountInvoiceInherit, self).search([('card_ids', '=', data.card_ids.id), ('state', '=', 'paid'), ])
            for rec in account_invoice_lines:
                # print rec.number
                available_point.append(rec.points_received)
                points_used.append(rec.points_used)
            result = sum(available_point) - sum(points_used)
            data.available_point = result + basic_points

    # @api.depends('invoice_line_ids.price_unit', 'card_ids')
    # def _get_points(self):
    #     for rec in self:
    #         if rec.card_ids:
    #             min_purchase_amount = rec.card_ids.type_id.rule_id.min_purchase_amount
    #             points = 0.0
    #             for line in rec.invoice_line_ids:
    #                 points += line.price_subtotal
    #             rec.points_received = points / min_purchase_amount

    @api.depends('invoice_line_ids.price_unit')
    def _get_points(self):
        for record in self:
            if record.card_ids:
                minimum_purcahse_amount = record.card_ids.type_id.rule_id.min_purchase_amount
                set_point = record.card_ids.type_id.rule_id.points
                points = 0.0
                for order in record:
                    for i in range(1, int(order.amount_total) + 1):
                        if i % minimum_purcahse_amount == 0:
                            points += set_point
                    order.update({
                        'points_received': points
                    })


    @api.multi
    @api.onchange('amount_total', 'points_used')
    def _discounted_amount(self):
        if self.amount_total and self.points_used:
            points_used = self.points_used
            amount_to_be_paid = self.amount_total
            available_points = self.available_point
            if points_used > available_points:
                raise ValidationError(_("Redeemable points should not exceed the available points."))
            else:
                result = amount_to_be_paid - points_used
                self.discounted_amount = result

    @api.constrains('points_used', 'available_point')
    def check_redeem_points(self):
        if self.points_used and self.available_point:
            if self.points_used > self.available_point:
                raise ValidationError(_("Redeemable points should not exceed the available points."))


class AccountPaymentInheritance(models.Model):
    _inherit = 'account.payment'
    use_point = fields.Boolean(string="Redeem Points",)
    available_points = fields.Char(string="Available point", )

    @api.model
    def default_get(self, fields):
        rec = super(AccountPaymentInheritance, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        print invoice_defaults
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['communication'] = invoice['reference'] or invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = invoice['residual']
            rec['available_points'] = invoice['available_point']
        return rec
