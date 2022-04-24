# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H#########Y#########P#########N#########O#########S##################

from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import api, fields, models,_
from odoo.addons.odoo_multi_channel_sale.tools import extract_list as EL


class ImportWoocommerceOrders(models.TransientModel):
    _name = 'import.woocommerce.orders'
    _inherit = 'import.orders'
    _description = "Import Woocommerce Orders"

    def import_now(self, **kwargs):
        data_list = []
        woocommerce = self._context.get('woocommerce')
        channel = self._context.get("channel_id")
        order_id = kwargs.get('woocommerce_object_id')
        import_order_date = kwargs.get('woocommerce_import_date_from')
        page_number = kwargs.get("page_number")
        page_size = kwargs.get("page_size")
        if order_id:
            url = "orders/%s" % order_id
            order = woocommerce.get(url).json()
            if "message" in order:
                message = "Error in importing orders : {}".format(order.get("message"))
                raise UserError(message)
            vals = self._get_order_by_id(woocommerce, channel, order)
            data_list.append(vals)
        elif import_order_date:
            data_list,last_added = self._filter_order_using_date(
                woocommerce, channel, **kwargs)
            kwargs["last_added"] = last_added
        else:
            data_list = self.get_order_all(woocommerce, channel, **kwargs)
        return data_list, kwargs

    def get_woocommerce_discount_lines(self,woocommerce,coupon_lines):
        amount = 0
        for line in coupon_lines:
            amount += float(line.get("discount"))
        return {
            'line_name': "Discount",
            'line_price_unit': float(amount),
            'line_product_uom_qty': 1,
            "line_source":"discount",
        }

    def get_woocommerce_order_line(self, woocommerce, channel, data):
        order_lines = []
        include_in_price = data["prices_include_tax"]
        line_items = data["line_items"]
        for line in line_items:
            product_id = line["product_id"]
            prod_env = self.env["import.woocommerce.products"].create({
                "channel_id":channel.id,
                "operation":"import"
            })
            feed_id = prod_env.woocommerce_create_product_feed(
                woocommerce,channel, product_id)
            if feed_id:
                _logger.info('Product feed created with ID : (%r)', feed_id)
            store_variant_id = line['variation_id']
            order_line_dict = {
                'line_name': line['name'],
                'line_price_unit': line['price'],
                'line_product_uom_qty': line['quantity'],
                'line_product_id': product_id,
                'line_taxes': self.env["import.woocommerce.taxes"].create({
                    "channel_id":channel.id,
                    "operation":"import"
                    }).get_woocommerce_taxes(woocommerce,line.get("taxes"), include_in_price)
            }
            if store_variant_id != 0:
                order_line_dict["line_variant_ids"] = store_variant_id
            order_lines.append((0, 0, order_line_dict))
        if data["coupon_lines"]:
            discount_line = self.get_woocommerce_discount_lines(woocommerce,data["coupon_lines"])
            order_lines.append((0,0,discount_line))
        return order_lines

    def get_order_all(self, woocommerce, channel, **kwargs):
        vals_list = []
        page_size = kwargs.get("page_number")
        page_number = kwargs.get("page_size")
        url = 'orders?page={}&per_page={}'.format(str(page_number), page_size)
        orders = woocommerce.get(url).json()
        if "message" in orders:
            message = "Error while importing orders : {}".format(orders["message"])
            _logger.info(message)
            if not kwargs.get("from_cron"):
                raise UserError(message)
        if orders:
            vals_list = list(map(lambda x: self._get_order_by_id(woocommerce,channel,x),orders))
        return vals_list

    def _filter_order_using_date(self, woocommerce, channel, **kwargs):
        if woocommerce:
            vals_list = []
            date_created = None
            import_order_date = kwargs.get("woocommerce_import_date_from")
            page_number = kwargs.get("page_number")
            page_size = kwargs.get("page_size")
            import_order_date = import_order_date.isoformat()
            url = 'orders?after={}&page={}&per_page={}'.format(import_order_date, str(page_number),page_size)
            orders = woocommerce.get(url).json()
            if "message" in orders:
                message = "Error while importing orders : {}".format(orders["message"])
                _logger.info(message)
                if not kwargs.get("from_cron"):
                    raise UserError(message)
            if orders:
                vals_list = list(map(lambda x: self._get_order_by_id(woocommerce,channel,x),orders))
                date_created = orders[-1].get("date_created")
            return vals_list, date_created

    def _get_woocommerce_shipping(self, shipping_line, include_in_price):
        shipping_list = []
        for shipping in shipping_line:
            shipping_line = {
                'line_name': "Shipping",
                'line_price_unit': shipping["total"],
                'line_product_uom_qty': 1,
                'line_source': 'delivery',
            }
            shipping_list.append((0, 0, shipping_line))
        return shipping_list

    def _get_order_by_id(self, woocommerce, channel, order):
        include_in_price = order['prices_include_tax']  
        order_lines = self.get_woocommerce_order_line(
            woocommerce, channel, order)
        if order['shipping_lines']:
            order_lines += self._get_woocommerce_shipping(
                order['shipping_lines'], include_in_price)
        method_title = 'Delivery'
        if order['shipping_lines']:
            method_title = order['shipping_lines'][0]['method_title']
        order_dict = {
            'store_id': order['id'],
            'channel_id': channel.id,
            "channel": channel.channel,
            'partner_id': order['customer_id'] or order['billing']['email'],
            'payment_method': order['payment_method_title'],
            'line_type': 'multi',
            'carrier_id': method_title,
            'line_ids': order_lines,
            'currency': order['currency'],
            'customer_name': order['billing']['first_name']+" "+order['billing']['last_name'],
            'customer_email': order['billing']['email'],
            'order_state': order['status'],
        }
        if order['billing']:
            order_dict.update({
                'invoice_partner_id': order['billing']['email'],
                'invoice_name': order['billing']['first_name']+" "+order['billing']['last_name'],
                'invoice_email': order['billing']['email'],
                'invoice_phone': order['billing']['phone'],
                'invoice_street': order['billing']['address_1'],
                'invoice_street2': order['billing']['address_2'],
                'invoice_zip': order['billing']['postcode'],
                'invoice_city': order['billing']['city'],
                'invoice_state_code': order['billing']['state'],
                'invoice_country_code': order['billing']['country'],
            })
        if order['shipping']:
            order_dict['same_shipping_billing'] = False
            order_dict.update({
                'shipping_partner_id': order['billing']['email'],
                'shipping_name': order['shipping']['first_name']+" "+order['billing']['last_name'],
                'shipping_street': order['shipping']['address_1'],
                'shipping_street2': order['shipping']['address_2'],
                'shipping_email': order['billing']['email'],
                'shipping_zip': order['shipping']['postcode'],
                'shipping_city': order['shipping']['city'],
                'shipping_state_code': order['shipping']['state'],
                'shipping_country_code': order['shipping']['country'],
            })
        return order_dict