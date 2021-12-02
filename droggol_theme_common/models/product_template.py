# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import api, fields, models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dr_label_id = fields.Many2one('dr.product.label', string='Label')
    dr_brand_id = fields.Many2one('dr.product.brand', string='Brand')
    dr_tag_ids = fields.Many2many('dr.product.tags', 'dr_product_tags_rel', 'product_id', 'tag_id', string='Tags')
    dr_tab_ids = fields.One2many('dr.product.tabs', 'product_id', string='Tabs', help='Display in product detail page on website.')
    dr_offer_ids = fields.One2many('dr.product.offer', 'product_id', string='Offers', help='Display in product detail page on website.')

    @api.onchange('website_id')
    def _onchange_website_id(self):
        self.dr_label_id = False
        self.dr_brand_id = False
        self.dr_tag_ids = False

    @api.model
    def _get_product_colors(self):
        color_variants = self.attribute_line_ids.filtered(lambda x: x.attribute_id.display_type == 'color')
        if len(color_variants) == 1:
            if len(color_variants.value_ids) == 1:
                return []
            return color_variants.value_ids.mapped('html_color')
        return []

    @api.model
    def _get_product_pricelist_offer(self):
        partner = self._context.get('partner')
        pricelist_id = self._context.get('pricelist')
        pricelist = self.env['product.pricelist'].browse(pricelist_id)

        price_rule = pricelist._compute_price_rule([(self, 1, partner)])
        price_rule_id = price_rule.get(self.id)[1]
        if price_rule_id:
            rule = self.env['product.pricelist.item'].browse([price_rule_id])
            if rule and rule.date_end:
                return {'rule': rule, 'date_end': rule.date_end.strftime('%Y-%m-%d %H:%M:%S')}
        return False
