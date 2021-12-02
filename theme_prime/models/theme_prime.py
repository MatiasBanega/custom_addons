# -*- coding: utf-8 -*-
from odoo import models


class ThemePrime(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_prime_post_copy(self, mod):
        pass
    
