# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    web_fb_pixel_key = fields.Char(related='website_id.web_fb_pixel_key', readonly=False)

    @api.depends('website_id')
    def visible_facebook_pixel(self):
        self.visible_facebook_pixel = bool(self.web_fb_pixel_key)

    def inverse_visible_facebook_pixel(self):
        if not self.visible_facebook_pixel:
            self.fb_pixel_key = False

    visible_facebook_pixel = fields.Boolean(
        string='Facebook Pixel',
        compute=visible_facebook_pixel,
        inverse=inverse_visible_facebook_pixel,
    )
