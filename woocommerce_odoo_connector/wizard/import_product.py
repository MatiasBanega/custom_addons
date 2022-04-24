#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H########Y#########P#########N#########O##########S##################
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.addons.odoo_multi_channel_sale.tools import remove_tags

class ImportWoocommerceProducts(models.TransientModel):
    _name = "import.woocommerce.products"
    _inherit = 'import.templates'
    _description = "Import Woocommerce Products"

    def _get_product_basics(self, woocommerce, channel, product_data):
        name = product_data.get("name")
        categ = ""
        store_id = product_data.get("id")
        default_code = product_data.get("sku")
        qty_available = product_data.get("stock_quantity")
        if product_data.get("images"):
            image_url = product_data.get("images")[0].get('src')
        list_price = product_data.get("price")
        for category in product_data['categories']:
            category_id = category['id']
            url = 'products/categories/%s' % category_id
            category_data = woocommerce.get(url).json()
            if "message" in category_data:
                message =  "Error in importing category : {}".format(category_data["message"])
                _logger.info(message)
            else:
                self._woocommerce_create_product_categories(
                    woocommerce, category_data)
            categ = categ+str(category['id'])+","

        length = product_data['dimensions'].get("length")
        width = product_data['dimensions'].get("width")
        height = product_data['dimensions'].get("height")
        weight = product_data.get("weight")
        description_sale = remove_tags(product_data.get("short_description"))
        description_purchase = remove_tags(product_data.get("description"))
        vals = dict(
            name=name,
            channel_id=channel.id,
            channel=channel.channel,
            store_id=store_id,
            list_price=list_price,
            extra_categ_ids=categ,
            length=length,
            width=width,
            height=height,
            weight=weight,
            description_sale=description_sale,
            description_purchase=description_purchase,
            image_url=image_url,
        )
        if default_code:
            vals["default_code"] = default_code
        if qty_available:
            vals["qty_available"] = qty_available
        return vals

    def get_product_all(self, woocommerce, channel, **kwargs):
        vals_list = []
        page_number = kwargs.get("page_number")
        page_size = kwargs.get("page_size")
        url = 'products?page={}&per_page={}'.format(str(page_number),page_size)
        products = woocommerce.get(url).json()
        if "message" in products:
            message = "Error in getting products : {}".format(products["message"])
            _logger.info(message)
            raise UserError(message)
        if products:
            vals_list = list(map(lambda x: self.get_product_by_id(woocommerce, channel,x),products))
        return vals_list

    def _woocommerce_create_product_categories(self, woocommerce, data):
        import_category_obj = self.env['import.woocommerce.categories'].create({
            "channel_id":self.channel_id.id,
            "operation":"import"
        })
        category_data = import_category_obj.get_category_vals(data)
        feed_obj = self.env['category.feed']
        feed_id = self.channel_id._create_feed(feed_obj, category_data)
        _logger.info("feed_id ======> %r",feed_id)

    def _get_feed_variants(self, woocommerce, channel, product_id, variation_ids):
        variant_list = []
        attribute_list = []
        image = False
        for variant_id in variation_ids:
            variant = woocommerce.get(
                'products/'+str(product_id)+"/variations/"+str(variant_id)).json()
            if "message" in variant:
                _logger.info("Error in getting Variants ===> %r",variant["message"])
                continue
            if variant['attributes']:
                attribute_list = []
                for attributes in variant['attributes']:
                    attrib_name_id = self.env['channel.attribute.mappings'].search([
                        ('store_attribute_name', '=', attributes['name']),
                        ('store_attribute_id', '=', attributes['id']),
                        ('channel_id', '=', channel.id)])

                    attrib_value_id = self.env['channel.attribute.value.mappings'].search([
                        ('channel_id', '=', channel.id),
                        ('store_attribute_value_name','=', attributes['option']),
                        ('attribute_value_name.attribute_id.id', '=', attrib_name_id.attribute_name.id)])
                    attr = {}
                    attr['name'] = str(attributes['name'])
                    attr['value'] = str(attributes['option'])
                    attr['attrib_name_id'] = attrib_name_id.store_attribute_id
                    attr['attrib_value_id'] = attrib_value_id.store_attribute_value_id
                    attribute_list.append(attr)
                    if isinstance(variant['image'], list):
                        image = variant['images'][0]['src']
                    else:
                        image = variant['image']['src']
            try:
                variant['price'] = float(variant['price'])
            except:
                pass
            variant_dict = {
                'image_url': image,
                'name_value': attribute_list,
                'store_id': variant['id'],
                'list_price': variant['price'],
                'qty_available': variant['stock_quantity'],
                'weight': variant['weight'] or "",
                # 'weight_unit'        : "kg",
                'length': variant['dimensions']['length'] or "",
                'width': variant['dimensions']['width'] or "",
                'height': variant['dimensions']['height'] or "",
                # 'dimension_unit'    : variant['dimensions']['unit'] or "",
            }
            if variant["sku"]:
                variant_dict['default_code']: variant['sku']
            variant_list.append(variant_dict)
        return variant_list

    def get_product_by_id(self, woocommerce, channel, product):
        vals = {}
        variants = []
        if product:
            product_basics = self._get_product_basics(
                woocommerce, channel, product)
            vals.update(product_basics)
            if product['type'] == 'variable':
                variation_ids = product['variations']
                variants = self._get_feed_variants(
                    woocommerce, channel, product['id'], variation_ids)
            vals.update(variants=variants)
            return vals

    def woocommerce_create_product_feed(self, woocommerce,channel_id,product_id):
        vals = {}
        url = 'products/%s' % product_id
        product = woocommerce.get(url).json()
        if "message" in product:
            _logger.info('Error:- %s' % product['message'])
            return False
        product_basics = self._get_product_basics(
            woocommerce, channel_id, product)
        vals.update(product_basics)
        if product['type'] == 'variable':
            variation_ids = product['variations']
            variants = self._get_feed_variants(
                woocommerce, channel_id, product['id'], variation_ids)
            variants = [(0,0,variant) for variant in variants]
            vals.update(feed_variants=variants)
        feed_obj = self.env['product.feed']
        feed_id = self.channel_id._create_feed(feed_obj, vals)
        return feed_id

    def import_now(self, **kwargs):
        data_list = []
        woocommerce = self._context.get('woocommerce')
        channel = self._context.get('channel_id')
        product_id = kwargs.get('woocommerce_object_id')
        if product_id:
            url = 'products/%s' % product_id
            product = woocommerce.get(url).json()
            if product.get('message'):
                _logger.info('Error:- %s' % product['message'])
                return data_list
            vals = self.get_product_by_id(woocommerce, channel, product)
            data_list.append(vals)
        elif kwargs.get('woocommerce_import_date_from'):
            data_list,last_added = self._filter_product_using_date(
                woocommerce, channel, **kwargs)
            kwargs["last_added"] = last_added
        else:
            data_list = self.get_product_all(woocommerce, channel, **kwargs)
        return data_list, kwargs

    def _filter_product_using_date(self, woocommerce, channel, **kwargs):
        if woocommerce:
            vals_list = []
            date_created = None
            product_import_date = kwargs.get("woocommerce_import_date_from")
            product_import_date = product_import_date.isoformat()
            page_number = kwargs.get("page_number")
            page_size = kwargs.get("page_size")
            url = 'products?after={}&page={}&per_page={}'.format(product_import_date, str(page_number), page_size)
            products = woocommerce.get(url).json()
            if "message" in products:
                _logger.info('ERROR:- %r', products['message'])
                if not kwargs.get("from_cron"):
                    raise UserError("Error in getting Product data :- {}".format(products.get("message")))
            if products:
                vals_list = list(map(lambda x: self.get_product_by_id(woocommerce, channel,x),products))
                date_created = products[-1].get("date_created")
            return vals_list,date_created
