# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    google_category_id = fields.Many2one(
        comodel_name='product.google.category',
        string='Google Category',
    )
