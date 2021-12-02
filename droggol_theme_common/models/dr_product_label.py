# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import api, fields, models


class DrProductLabel(models.Model):
    _name = 'dr.product.label'
    _description = 'Product Label'

    name = fields.Char(required=True, translate=True)
    color = fields.Selection([
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('orange', 'Orange'),
        ('red', 'Red'),
        ('gray', 'Gray'),
        ('black', 'Black'),
    ])
    style = fields.Selection([
        ('1', 'Tag'),
        ('2', 'Badge'),
        ('3', 'Circle'),
    ], default='1', required=True)
    product_ids = fields.One2many('product.template', 'dr_label_id')
    product_count = fields.Integer(compute='_compute_product_count')
    active = fields.Boolean(default=True)

    def _compute_product_count(self):
        for label in self:
            label.product_count = len(label.product_ids)

    def action_open_products(self):
        self.ensure_one()
        action = self.env.ref('website_sale.product_template_action_website').read()[0]
        action['domain'] = [('dr_label_id', '=', self.id)]
        return action
