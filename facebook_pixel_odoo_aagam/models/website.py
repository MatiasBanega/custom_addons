# -*- coding: utf-8 -*-

from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    web_fb_pixel_key = fields.Char('Facebook Pixel ID')
