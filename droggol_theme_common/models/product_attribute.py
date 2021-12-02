# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import api, fields, models


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    display_type = fields.Selection(
        selection_add=[
            ('radio_circle', 'Radio Circle'),
            ('radio_square', 'Radio Square'),
            ('radio_image', 'Radio Image'),
        ], ondelete={'radio_circle': 'cascade', 'radio_square': 'cascade', 'radio_image': 'cascade'})
    dr_is_hide_shop_filter = fields.Boolean('Hide in Shop Filter', default=False)
    dr_is_show_shop_search = fields.Boolean('Show Searchbar in Shop Filter', default=False)


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    dr_image = fields.Binary(string='Image')


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    dr_image = fields.Binary('Image', related='product_attribute_value_id.dr_image')
