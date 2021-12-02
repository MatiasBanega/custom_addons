# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import api, fields, models


class DrProductTabs(models.Model):
    _name = 'dr.product.tabs'
    _description = 'Product Tabs'
    _order = 'sequence,id'

    name = fields.Char(string='Title', required=True, translate=True)
    icon = fields.Char(default='list')
    content = fields.Html(sanitize_attributes=False, translate=True)
    sequence = fields.Integer(string='Sequence')
    product_id = fields.Many2one('product.template')
    tag_id = fields.Many2one('dr.product.tags')


class DrProductOffer(models.Model):
    _name = 'dr.product.offer'
    _description = 'Product Offers'
    _order = 'sequence,id'

    name = fields.Char(string='Title', required=True, translate=True)
    description = fields.Char(string='Description', required=True, translate=True)
    icon = fields.Char(default='list')
    sequence = fields.Integer(string='Sequence')
    dialog_content = fields.Html(sanitize_attributes=False, translate=True)
    product_id = fields.Many2one('product.template')
    tag_id = fields.Many2one('dr.product.tags')
