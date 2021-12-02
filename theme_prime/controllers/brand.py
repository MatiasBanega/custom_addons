# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

import string
from collections import defaultdict
from odoo import http
from odoo.http import request


class ThemePrimeBrand(http.Controller):

    @http.route('/shop/all_brands', type='http', auth='public', website=True)
    def all_brands(self, **args):
        brands = request.env['dr.product.brand'].search(request.website.website_domain())
        is_disable_grouping = request.website._get_dr_theme_config('json_brands_page')['disable_brands_grouping']

        if is_disable_grouping:
            brands_group_by_alphabet = {'All Brands': brands}
        else:
            alphabet_range = string.ascii_uppercase
            brands_group_by_alphabet = defaultdict(list)
            brands_group_by_alphabet.update((alphabet, []) for alphabet in alphabet_range)
            for brand in brands:
                first_char = str.upper(brand.name[:1])
                brands_group_by_alphabet[first_char].append(brand)

        return request.render('theme_prime.all_brands', {
            'is_disable_grouping': is_disable_grouping,
            'grouped_brands': brands_group_by_alphabet
        })
