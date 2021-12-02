# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import api, fields, models


class DrProductBrand(models.Model):
    _name = 'dr.product.brand'
    _inherit = ['website.multi.mixin']
    _description = 'Product Brand'
    _order = 'sequence,id'

    name = fields.Char(required=True, translate=True)
    description = fields.Char(translate=True)
    image = fields.Binary()
    product_ids = fields.One2many('product.template', 'dr_brand_id')
    product_count = fields.Integer(compute='_compute_product_count')
    sequence = fields.Integer(string='Sequence')
    active = fields.Boolean(default=True)

    def _compute_product_count(self):
        for brand in self:
            brand.product_count = len(brand.product_ids)

    def action_open_products(self):
        self.ensure_one()
        action = self.env.ref('website_sale.product_template_action_website').read()[0]
        action['domain'] = [('dr_brand_id', '=', self.id)]
        return action

    @api.model
    def reorder_sequence(self):
        sequence = 1
        for brand in self.env['dr.product.brand'].search([], order='name'):
            brand.sequence += sequence
            sequence += 1
