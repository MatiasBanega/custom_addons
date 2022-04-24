# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H#########Y#########P#########N#########O#########S###################
import sys
import logging
_logger = logging.getLogger(__name__)
try:
    from woocommerce import API
except ImportError:
    _logger.info(
        '**Please Install Woocommerce Python Api=>(cmd: pip3 install woocommerce)')
from datetime import datetime, timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons.odoo_multi_channel_sale.tools import extract_list as EL
from odoo.tools.translate import _


class MultiChannelSale(models.Model):
    _inherit = "multi.channel.sale"

    woocommerce_url = fields.Char(string="URI", help='eg. http://xyz.com')
    woocommerce_consumer_key = fields.Char(
        string='Consumer Key',
        help='eg. ck_ccac94fc4362ba12a2045086ea9db285e8f02ac9',
    )
    woocommerce_secret_key = fields.Char(
        help='eg. cs_a4c0092684bf08cf7a83606b44c82a6e0d8a4cae')

    @api.model
    def get_channel(self):
        channel_names = super(MultiChannelSale, self).get_channel()
        channel_names.append(('woocommerce', 'WooCommerce'))
        return channel_names

    def get_core_feature_compatible_channels(self):
        vals = super().get_core_feature_compatible_channels()
        vals.append('woocommerce')
        return vals

    def connect_woocommerce(self):
        message = ""
        woocommerce = API(
            url=self.woocommerce_url,
            consumer_key=self.woocommerce_consumer_key,
            consumer_secret=self.woocommerce_secret_key,
            wp_api=True,
            version="wc/v2",
            timeout=40,
            query_string_auth=True,
            # verify_ssl        =    False,
        )
        try:
            woocommerce_api = woocommerce.get('system_status').json()
        except Exception as e:
            raise UserError(_("Error:"+str(e)))
        if 'message' in woocommerce_api:
            message = "Connection Error" + \
                str(woocommerce_api['data']['status']) + \
                " : "+str(woocommerce_api["message"])
            raise UserError(_(message))
        else:
            self.state = 'validate'
            message = "Connection Successful!!"
        return True, message

    def get_woocommerce_connection(self):
        try:
            woocommerce = API(
                url=self.woocommerce_url,
                consumer_key=self.woocommerce_consumer_key,
                consumer_secret=self.woocommerce_secret_key,
                wp_api=True,
                version="wc/v2",
                timeout=40,
                query_string_auth=True,
                # verify_ssl        =    False,
            )
        except ImportError:
            raise UserError("**Please Install Woocommerce Python Api=>(cmd: pip3 install woocommerce)")
        return woocommerce

#---------------------------------------Import Process ---------------------------------------------------------

    def import_woocommerce(self, object, **kwargs):
        woocommerce = self.get_woocommerce_connection()
        data_list = []
        # kwargs["page_size"] = sys.maxsize
        if woocommerce:
            if object == 'product.category':
                data_list,kwargs = self.import_woocommerce_categories(
                    woocommerce, **kwargs)
            elif object == 'res.partner':
                data_list, kwargs = self.import_woocommerce_customers(
                    woocommerce, **kwargs)
            elif object == 'product.template':
                data_list, kwargs = self.import_woocommerce_products(
                    woocommerce, **kwargs)
            elif object == 'sale.order':
                data_list, kwargs = self.import_woocommerce_orders(
                    woocommerce, **kwargs)
            elif object == "delivery.carrier":
                data_list,kwargs = self.import_woocommerce_shipping(
                    woocommerce, **kwargs)
            return data_list, kwargs

    def import_woocommerce_shipping(self, woocommerce, **kwargs):
        vals = dict(
            channel_id = self.id,
            operation = "import"
        )
        obj = self.env["import.woocommerce.shipping"].create(vals)
        return obj.with_context({
            "woocommerce":woocommerce,
            "channel_id":self,
        }).import_now(**kwargs)

    def import_woocommerce_categories(self, woocommerce, **kwargs):
        vals = dict(
            channel_id=self.id,
            operation='import',
        )
        obj = self.env['import.woocommerce.categories'].create(vals)
        return obj.with_context({
            "woocommerce": woocommerce,
            "channel_id": self,
        }).import_now(**kwargs)

    def import_woocommerce_customers(self, woocommerce, **kwargs):
        vals = dict(
            channel_id=self.id,
            operation='import',
        )
        obj = self.env['import.woocommerce.partners'].create(vals)
        return obj.with_context({
            "woocommerce": woocommerce,
            "channel_id": self,
        }).import_now(**kwargs)

    def import_woocommerce_products(self, woocommerce, **kwargs):
        vals = dict(
            channel_id=self.id,
            operation='import',
        )
        self.env['import.woocommerce.attributes'].with_context({
            "channel_id": self,
            "woocommerce": woocommerce,
        }).import_woocommerce_attribute()
        obj = self.env['import.woocommerce.products'].create(vals)
        return obj.with_context({
            "woocommerce": woocommerce,
            'channel_id': self,
        }).import_now(**kwargs)

    def import_woocommerce_orders(self, woocommerce, **kwargs):
        vals = dict(
            channel_id=self.id,
        )
        obj = self.env['import.woocommerce.orders'].create(vals)
        return obj.with_context({
            'woocommerce': woocommerce,
            'channel_id': self,
        }).import_now(**kwargs)

# ----------------------------------------------Export Process -------------------------------------------

    def export_woocommerce(self, record):
        woocommerce = self.get_woocommerce_connection()
        data_list = []
        if woocommerce:
            if record._name == 'product.category':
                initial_record_id = record.id
                data_list = self.export_woocommerce_categories(
                    woocommerce, record, initial_record_id)
            elif record._name == 'product.template':
                data_list = self.export_woocommerce_product(
                    woocommerce, record)
            return data_list

    def export_woocommerce_categories(self, woocommerce, record, initial_record_id):
        vals = dict(
            channel_id=self.id,
            operation='export',
        )
        obj = self.env['export.categories'].create(vals)
        return obj.with_context({
            'woocommerce': woocommerce,
            'channel_id': self,
        }).woocommerce_export_now(record, initial_record_id)

    def export_woocommerce_product(self, woocommerce, record):
        vals = dict(
            channel_id=self.id,
            operation='export',
        )
        obj = self.env['export.templates'].create(vals)
        return obj.with_context({
            'woocommerce': woocommerce,
            'channel_id': self,
        }).woocommerce_export_now(record)

#---------------------------------------Update Process -------------------------------------------

    def update_woocommerce(self, record, get_remote_id):
        woocommerce = self.get_woocommerce_connection()
        data_list = []
        if woocommerce:
            remote_id = get_remote_id(record)
            if record._name == 'product.category':
                initial_record_id = record.id
                data_list = self.update_woocommerce_categories(
                    woocommerce, record, initial_record_id, remote_id)
            elif record._name == 'product.template':
                data_list = self.update_woocommerce_product(
                    woocommerce, record, remote_id)
            return data_list

    def update_woocommerce_categories(self, woocommerce, 
        record, initial_record_id, remote_id):
        vals = dict(
            channel_id=self.id,
            operation='export',
        )
        obj = self.env['export.categories'].create(vals)
        return obj.with_context({
            'woocommerce': woocommerce,
            'channel_id': self,
        }).woocommerce_update_now(record, initial_record_id, remote_id)

    def update_woocommerce_product(self, woocommerce, record, remote_id):
        vals = dict(
            channel_id=self.id,
            operation='export',
        )
        obj = self.env['export.templates'].create(vals)
        return obj.with_context({
            'woocommerce': woocommerce,
            'channel_id': self,
        }).woocommerce_update_now(record, remote_id)

#----------------------------------- Core Methods -----------------------------------------------
    def woocommerce_post_do_transfer(self, stock_picking, mapping_ids, result):
        order_status = self.order_state_ids.filtered('odoo_ship_order')
        if order_status:
            order_status = order_status[0]
            status = order_status.channel_state
            woocommerce_order_id = mapping_ids.store_order_id
            wcapi = self.get_woocommerce_connection()
            data = wcapi.get('orders/'+woocommerce_order_id).json()
            data.update({'status': status})
            msg = wcapi.put('orders/'+woocommerce_order_id, data)

    def woocommerce_post_confirm_paid(self, invoice, mapping_ids, result):
        order_status = self.order_state_ids.filtered(
            lambda state: state.odoo_set_invoice_state == 'paid')
        if order_status:
            order_status = order_status[0]
            status = order_status.channel_state
            woocommerce_order_id = mapping_ids.store_order_id
            wcapi = self.get_woocommerce_connection()
            data = wcapi.get('orders/'+woocommerce_order_id).json()
            data.update({'status': status})
            msg = wcapi.put('orders/'+woocommerce_order_id, data)
    
    def woocommerce_post_cancel_order(self, sale_order, mapping_ids, result):
        order_status = self.order_state_ids.filtered(
            lambda order_state_id: order_state_id.odoo_order_state == 'cancelled')
        if order_status:
            order_status = order_status[0]
            status = order_status.channel_state
            woocommerce_order_id = mapping_ids.store_order_id
            wcapi = self.get_woocommerce_connection()
            data = wcapi.get('orders/'+woocommerce_order_id).json()
            data.update({'status': status})
            msg = wcapi.put('orders/'+woocommerce_order_id, data)

    def sync_quantity_woocommerce(self, mapping, qty):
        woocommerce = self.get_woocommerce_connection()
        return self.env['export.templates'].update_woocommerce_quantity(woocommerce, qty, mapping)

# ---------------------------CRON OPERATIONS ---------------------------------------

    def woocommerce_import_order_cron(self):
        kw = dict(
            object="sale.order",
            woocommerce_import_date_from=self.import_order_date,
            from_cron = True
        )
        self.env["import.operation"].create({
            "channel_id":self.id 
        }).import_with_filter(**kw)

    def woocommerce_import_product_cron(self):
        kw = dict(
            object="product.template",
            woocommerce_import_date_from=self.import_product_date,
            from_cron = True
        )
        self.env["import.operation"].create({
            "channel_id":self.id 
        }).import_with_filter(**kw)

    def woocommerce_import_partner_cron(self):
        kw = dict(
            object="res.partner",
            woocommerce_import_date_from=self.import_customer_date,
            from_cron = True
        )
        self.env["import.operation"].create({
            "channel_id":self.id 
        }).import_with_filter(**kw)

    def woocommerce_import_category_cron(self):
        kw = dict(
            object="product.category",
        )
        self.env["import.operation"].create({
            "channel_id":self.id 
        }).import_with_filter(**kw)