# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _


class CardType(models.Model):
    _name = 'card.type'
    _rec_name = 'name'
    _description = 'Loyalty Card Type'
    _order = 'name'

    name = fields.Char(
        string='Type Name',
        required=True)
    # point_per_period = fields.Float(
    #     string='Points per Period',
    #     digits=dp.get_precision('Discount'))
    period_id = fields.Many2one(
        string='Period',
        comodel_name='card.period',
        required=1)
    categ_id = fields.Many2one(
        string='Category',
        comodel_name='card.category',
        required=1)
    rule_id = fields.Many2one(
        string='Rule',
        comodel_name='card.rule',
        required=1)
    basic_point = fields.Float(
        string='Basic Points',
        required=1,
        default=0.0,
        digits=dp.get_precision('Discount'))
    issue_hard_card = fields.Boolean(
        string='Is Issue Hard Card?',
        default=True)
    note = fields.Text(
        string='Note')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('activated', 'Activated'),
        ('deactivated', 'Deactivated'),
        ('locked', 'Locked'),
    ], string='Status', readonly=True, default='draft', )


    @api.multi
    def btn_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    @api.multi
    def btn_activate(self):
        for rec in self:
            rec.write({'state': 'activated'})

    @api.multi
    def btn_deactivate(self):
        for rec in self:
            rec.write({'state': 'deactivated'})

    @api.multi
    def btn_lock(self):
        for rec in self:
            rec.write({'state': 'locked'})

    _sql_constraints = [
        ('uniq_name', "unique(name)",
         _('Card Type has been existed. Please pick another name for this card type!'))]


#
# _sql_constraints = [
#     ('uniq_name_period_categ', "unique(name,period_id,categ_id)",
#      _('Name/Period/Category value has been existed!')),
#     ('uniq_seq_categ', "unique(seq,categ_id)",
#      _('Sequence/Category value has been existed!'))]
#
#
# @api.multi
# def name_get(self):
#     result = []
#     for r in self:
#         name = u"{} - {}".format(r.name, r.period_id.name)
#         result.append((r.id, name))
#     return result
#
#
# @api.multi
# def _get_next_type(self):
#     self.ensure_one()
#     args = [('categ_id', '=', self.categ_id.id),
#             ('seq', '>', self.seq)]
#     type = self.search(args, limit=1, order='seq')
#     return type
