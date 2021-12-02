# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)


import logging
import json

from odoo import _, api, fields, models, tools

from odoo.http import request


_logger = logging.getLogger(__name__)


class DrThemeConfig(models.Model):

    _name = 'dr.theme.config'
    _description = 'Droggol Theme Config'
    _rec_name = "key"

    key = fields.Char(required=True)
    value = fields.Char()
    website_id = fields.Many2one('website')

    @api.model_create_multi
    def create(self, vals_list):
        self.clear_caches()
        return super(DrThemeConfig, self).create(vals_list)

    def write(self, vals):
        self.clear_caches()
        res = super(DrThemeConfig, self).write(vals)
        return res

    @api.model
    @tools.ormcache('website_id')
    def _get_all_config(self, website_id):
        result_configs = self._get_default_theme_config(website_id)
        all_config = self.search([('website_id', '=', website_id)])
        for config in all_config:
            try:
                if config.key.startswith('bool_'):
                    result_configs[config.key] = config.value == 'True'
                elif config.key.startswith('json_'):
                    config_value = json.loads(config.value)
                    if isinstance(config_value, dict):
                        result_configs[config.key].update(config_value)
                    else:
                        result_configs[config.key] = config_value
                elif config.key.startswith('int_'):
                    result_configs[config.key] = int(config.value)
                elif config.key.startswith('float_'):
                    result_configs[config.key] = float(config.value)
                else:
                    result_configs[config.key] = config.value
            except json.decoder.JSONDecodeError:
                _logger.warning("Theme Prime Config: Cannot parse '%s' with value '%s' ", config.key, config.value)
            except ValueError:
                _logger.warning("Theme Prime Config: Cannot parse '%s' with value '%s' ", config.key, config.value)
        return result_configs

    def _get_default_theme_config(self, website_id):
        website = self.env['website'].sudo().browse(website_id)

        # TODO: Clear cache on website write (when theme is installed)

        return {
            'bool_enable_ajax_load': False,
            'bool_show_bottom_bar_onscroll': False,
            'bool_display_bottom_bar': True,
            'bool_mobile_filters': True,
            'json_zoom': {
                'zoom_enabled': True,
                'zoom_factor': 2,
                'disable_small': False
            },
            'json_category_pills': {
                'enable': True,
                'enable_child': True,
                'hide_desktop': True,
                'show_title': True,
                'style': 1,
            },
            'json_grid_product': {
                'show_color_preview': True,
                'show_quick_view': True,
                'show_similar_products': True,
                'show_rating': True,
            },
            'json_shop_filters': {
                'in_sidebar': False,
                'collapsible': True,
                'show_category_count': True,
                'show_attrib_count': False,
                'hide_attrib_value': False,
                'show_price_range_filter': True,
                'price_range_display_type': 'sales_price',
                'show_rating_filter': True,
                'show_brand_search': True,
                'show_labels_search': True,
                'show_tags_search': True,
                'brands_style': 1,
                'tags_style': 1,
            },
            'bool_sticky_add_to_cart': True,
            'bool_general_show_category_search': True,
            'json_general_language_pricelist_selector': {
                'hide_country_flag': False,
            },
            'json_brands_page': {
                'disable_brands_grouping': False,
            },
            'cart_flow': 'default',
            'json_bottom_bar_config': ['tp_home', 'tp_search', 'tp_wishlist', 'tp_offer', 'tp_brands', 'tp_category', 'tp_orders'],
            'theme_installed': website.theme_id and website.theme_id.name.startswith('theme_prime') or False,
            'pwa_active': website.dr_pwa_activated,
            'bool_product_offers': True,
        }

    def _save_config(self, website_id, configs):
        all_config = self.search([('website_id', '=', website_id)])
        for key, value in configs.items():
            key, value = self._prepare_value_for_write(key, value)
            config = all_config.filtered(lambda c: c.key == key)
            if config:
                config.value = value
            else:
                self.create({'key': key, 'value': value, 'website_id': website_id})
        return True

    def _prepare_value_for_write(self, key, value):
        if key.startswith('json_'):
            value = json.dumps(value)
        elif key.startswith('int_'):
            value = value
        return key.strip(), value


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    @api.model
    def get_dr_theme_config(self):
        result = {}
        if request.website:
            result = request.website._get_dr_theme_config()
        return result
