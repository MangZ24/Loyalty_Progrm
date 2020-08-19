from addons.account.models.account_invoice import AccountInvoice
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SalesOrderInherit(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"
    _description = 'Sales Order Inherit'

    card_ids = fields.Many2one(string="Loyalty Card", comodel_name="card.card", search="_search_by_card")
    card_number = fields.Char(compute="_get_card_number", store=True)
    converted_points = fields.Float(string="Points", store=True, readonly=True, compute="_get_points")
    available_points = fields.Float(string="Available Points", compute="_get_available_points")

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

    # @api.depends('order_line.price_total')
    # def _get_points(self):
    #     if self.card_ids:
    #         min_purchase_amount = self.card_ids.type_id.rule_id.min_purchase_amount
    #         for order in self:
    #             points = 0.0
    #             for line in order.order_line:
    #                 points += line.price_subtotal
    #                 order.update({
    #                     'converted_points': min_purchase_amount % points
    #                 })

    @api.depends('order_line.price_total')
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
                        'converted_points': points
                    })


    @api.multi
    @api.depends('card_ids')
    def _get_available_points(self):
        if self.card_ids:
            invoice = self.env['account.invoice'].search(
                [('card_number', '=', self.card_ids.card_number), ('state', '=', 'paid')])
            basic_points = self.card_ids.type_id.basic_point
            print invoice
            if invoice:
                for r in invoice:
                    self.available_points = r.points_received + basic_points
            else:
                self.available_points = basic_points

    def _get_card_number(self):
        for record in self:
            if record.card_ids:
                card_number = record.env['card.card'].search([('id', '=', record.card_ids.id)])
                for card in card_number:
                    record.card_number = card.card_number

    # overwrite function and add custom codes
    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                order.force_quotation_send()
            order.order_line._action_procurement_create()
            if order.card_ids:
                v = self.env['card.history.lines'].create({
                    'card_id': order.card_ids.id,
                    'card_number': order.card_ids.card_number,
                    'sale_order': order.name,
                    'point_recieved': order.converted_points,
                })
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return True

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        if self.card_ids:
            invoice_vals = {
                'name': self.client_order_ref or '',
                'origin': self.name,
                'type': 'out_invoice',
                'account_id': self.partner_invoice_id.property_account_receivable_id.id,
                'partner_id': self.partner_invoice_id.id,
                'partner_shipping_id': self.partner_shipping_id.id,
                'journal_id': journal_id,
                'currency_id': self.pricelist_id.currency_id.id,
                'comment': self.note,
                'payment_term_id': self.payment_term_id.id,
                'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
                'company_id': self.company_id.id,
                'user_id': self.user_id and self.user_id.id,
                'team_id': self.team_id.id,
                'card_ids': self.card_ids.id,
                'points_received': self.converted_points,
            }
            print invoice_vals
        else:
            invoice_vals = {
                'name': self.client_order_ref or '',
                'origin': self.name,
                'type': 'out_invoice',
                'account_id': self.partner_invoice_id.property_account_receivable_id.id,
                'partner_id': self.partner_invoice_id.id,
                'partner_shipping_id': self.partner_shipping_id.id,
                'journal_id': journal_id,
                'currency_id': self.pricelist_id.currency_id.id,
                'comment': self.note,
                'payment_term_id': self.payment_term_id.id,
                'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
                'company_id': self.company_id.id,
                'user_id': self.user_id and self.user_id.id,
                'team_id': self.team_id.id,
            }
        return invoice_vals
