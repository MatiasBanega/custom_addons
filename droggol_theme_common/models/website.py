# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

import base64

from odoo import _, fields, models, tools, api
from odoo.osv import expression
from odoo.modules.module import get_resource_path


class Website(models.Model):
    _inherit = 'website'

    def _default_footer_logo(self):
        image_path = get_resource_path('website', 'static/src/img', 'website_logo.png')
        with tools.file_open(image_path, 'rb') as f:
            return base64.b64encode(f.read())

    dr_sale_special_offer = fields.Html(sanitize_attributes=False, translate=True)

    # PWA
    dr_pwa_activated = fields.Boolean()
    dr_pwa_name = fields.Char()
    dr_pwa_short_name = fields.Char()
    dr_pwa_background_color = fields.Char(default='#000000')
    dr_pwa_theme_color = fields.Char(default='#FFFFFF')
    dr_pwa_icon_192 = fields.Binary()
    dr_pwa_icon_512 = fields.Binary()
    dr_pwa_start_url = fields.Char(default='/shop')
    dr_pwa_offline_page = fields.Boolean()
    dr_pwa_version = fields.Integer(default=1)
    dr_pwa_shortcuts = fields.One2many('dr.pwa.shortcuts', 'website_id')

    def _get_dr_theme_config(self, key=False):
        """ See dr.theme.config for more info"""
        self.ensure_one()
        website_config = self.env['dr.theme.config']._get_all_config(self.id)
        website_config['is_public_user'] = not self.env.user.has_group('website.group_website_publisher')
        if key:
            return website_config.get(key)
        return website_config

    def _get_theme_prime_shop_config(self):
        Website = self.get_current_website()
        result = {
            'is_rating_active': Website.viewref('website_sale.product_comment').active,
            'is_buy_now_active': Website.viewref('website_sale.product_buy_now').active,
            'is_multiplier_active': Website.viewref('website_sale.product_quantity').active,
            'is_wishlist_active': Website.viewref('website_sale_wishlist.add_to_wishlist').active,
            'is_comparison_active': Website.viewref('website_sale_comparison.add_to_compare').active,
            'is_wishlist_installed': False,
            'is_compare_installed': False,
        }
        modules = self.env['ir.module.module'].sudo().search(expression.OR([[('name', '=', 'website_sale_wishlist')], [('name', '=', 'website_sale_comparison')]]))
        for module in modules:
            if module.state == 'installed':
                if module.name == 'website_sale_comparison':
                    result['is_compare_installed'] = True
                if module.name == 'website_sale_wishlist':
                    result['is_wishlist_installed'] = True
        return result

    def _get_website_category(self):
        return self.env['product.public.category'].search([('website_id', 'in', [False, self.id]), ('parent_id', '=', False)])

    def _get_theme_prime_rating_template(self, rating_avg, rating_count=False):
        return self.env["ir.ui.view"]._render_template('theme_prime.d_rating_widget_stars_static', values={
            'rating_avg': rating_avg,
            'rating_count': rating_count,
        })

    @api.model
    def get_theme_prime_bottom_bar_action_buttons(self):
        # Add to cart, blog, checkout, pricelist, language,
        return {
            'tp_home': {'name': _("Home"), 'url': '/', 'icon': 'fa fa-home'},
            'tp_search': {'name': _("Search"), 'icon': 'dri dri-search', 'action_class': 'tp-search-sidebar-action'},
            'tp_wishlist': {'name': _("Wishlist"), 'icon': 'dri dri-wishlist', 'url': '/shop/wishlist'},
            'tp_offer': {'name': _("Offers"), 'url': '/offers', 'icon': 'dri dri-bolt'},
            'tp_brands': {'name': _("Brands"), 'icon': 'dri dri-tag-l ', 'url': '/shop/all_brands'},
            'tp_category': {'name': _("Category"), 'icon': 'dri dri-category', 'action_class': 'tp-category-action'},
            'tp_orders': {'name': _("Orders"), 'icon': 'fa fa-file-text-o', 'url': '/my/orders'},
            'tp_cart': {'name': _("Cart"), 'icon': 'dri dri-cart', 'url': '/shop/cart'},
            'tp_lang_selector': {'name': _("Language and Pricelist selector")},
        }

    def _convert_currency_price(self, amount, from_base_currency=True, rounding_method=None):
        """ This function converts amount based website pricelist and company company currency

            :param amount: float or int,
            :param from_base_currency:  If True then coverts amount from company currency to pricelist currency
                                        else it converts pricelist currency to company currency
            :param rounding_method:  funcation reference to round the final amount
        """
        base_currency = self.company_id.currency_id
        pricelist_currency = self.get_current_pricelist().currency_id
        if base_currency != pricelist_currency:
            if from_base_currency:
                amount = base_currency._convert(amount, pricelist_currency, self.company_id, fields.Date.today())
            else:
                amount = pricelist_currency._convert(amount, base_currency, self.company_id, fields.Date.today())
        return rounding_method(amount) if rounding_method else amount


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # PWA
    dr_pwa_activated = fields.Boolean(related='website_id.dr_pwa_activated', readonly=False)
    dr_pwa_name = fields.Char(related='website_id.dr_pwa_name', readonly=False)
    dr_pwa_short_name = fields.Char(related='website_id.dr_pwa_short_name', readonly=False)
    dr_pwa_background_color = fields.Char(related='website_id.dr_pwa_background_color', readonly=False)
    dr_pwa_theme_color = fields.Char(related='website_id.dr_pwa_theme_color', readonly=False)
    dr_pwa_icon_192 = fields.Binary(related='website_id.dr_pwa_icon_192', readonly=False)
    dr_pwa_icon_512 = fields.Binary(related='website_id.dr_pwa_icon_512', readonly=False)
    dr_pwa_start_url = fields.Char(related='website_id.dr_pwa_start_url', readonly=False)
    dr_pwa_shortcuts = fields.One2many(related='website_id.dr_pwa_shortcuts', readonly=False)
    dr_pwa_offline_page = fields.Boolean(related='website_id.dr_pwa_offline_page', readonly=False)

    def dr_open_pwa_shortcuts(self):
        self.website_id._force()
        action = self.env.ref('droggol_theme_common.dr_pwa_shortcuts_action').read()[0]
        action['domain'] = [('website_id', '=', self.website_id.id)]
        action['context'] = {'default_website_id': self.website_id.id}
        return action
