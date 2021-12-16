# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_analytics_4_key = fields.Char(
        related='website_id.google_analytics_4_key',
        readonly=False,
    )

    @api.depends('website_id')
    def has_google_analytics_4(self):
        self.has_google_analytics_4 = bool(self.google_analytics_4_key)

    def inverse_has_google_analytics_4(self):
        if not self.has_google_analytics_4:
            self.google_analytics_4_key = False

    has_google_analytics_4 = fields.Boolean(
        string='Google Analytics 4',
        compute=has_google_analytics_4,
        inverse=inverse_has_google_analytics_4,
    )

