# -*- coding: utf-8 -*-

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    google_analytics_4_key = fields.Char('Google Analytics 4 ID')

