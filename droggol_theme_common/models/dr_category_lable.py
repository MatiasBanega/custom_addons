# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import fields, models


class DrWebsiteCategoryLabel(models.Model):
    _name = 'dr.product.public.category.label'
    _description = 'Category Label'

    name = fields.Char(required=True, translate=True)
    color = fields.Selection([('green', 'Green'), ('blue', 'Blue'), ('red', 'Red'), ('orange', 'Orange'), ('gray', 'Gray'), ('black', 'Black')])
    category_ids = fields.One2many('product.public.category', 'dr_category_label_id')
    category_count = fields.Integer(compute='_compute_category_count')

    def _compute_category_count(self):
        for label in self:
            label.category_count = len(label.category_ids)

    def action_open_category(self):
        self.ensure_one()
        action = self.env.ref('website_sale.product_public_category_action').read()[0]
        action['domain'] = [('dr_category_label_id', '=', self.id)]
        action['context'] = {}
        return action


class DrProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    dr_category_label_id = fields.Many2one('dr.product.public.category.label', string='Label')
    dr_category_cover_image = fields.Binary(string='Cover Image')
