# -*- coding: utf-8 -*-
#################################################################################
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H#########Y#########P#########N#########O#########S###################
from urllib import parse as urlparse
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError


class UpdateWoocommerceProducts(models.TransientModel):
    _inherit = "export.templates"

    def woocommerce_update_now(self, record, remote_id):
        channel = self._context.get('channel_id')
        woocommerce = self._context.get('woocommerce')
        response = self.woocommerce_update_template(
            woocommerce, channel, record, remote_id)
        return [True, response]

    def woocommerce_update_template(self, woocommerce, channel, template_record, remote_id):
        if len(template_record.product_variant_ids)>1:
            return_list = self.update_woocommerce_variable_product(
                woocommerce, channel, template_record, remote_id)
            data_list = return_list
        else:
            returnid = self.update_woocommerce_simple_product(
                woocommerce, channel, template_record, remote_id)
            data_list = (returnid, [])
        return data_list

    def update_woocommerce_image_path(self, name, product):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        image_url = '/channel/image/product.product/%s/image_1920/492x492.png' % (
            product.id)
        full_image_url = '%s' % urlparse.urljoin(base_url, image_url)
        return full_image_url, name

    def update_woocommerce_product_image(self, template, variant=False):
        if template.image_1920:
            image_list = []
            count = 0
            template_url, name = self.update_woocommerce_image_path(
                template.name, template.product_variant_ids[0])
            image_list.append({
                'src'		: template_url,
                'name'		: name,
                'position'	: 0,
            })
            if variant:
                for variation in template.product_variant_ids:
                    count += 1
                    variant_url, name = self.update_woocommerce_image_path(
                        variation.name+str(count), variation)
                    image_list.append({
                        'src'		: variant_url,
                        'name'		: name,
                        'position'	: count,
                    })
            return image_list

    def update_woocommerce_attribute_dict(self, woocommerce, channel, variant):
        attribute_dict = []
        if variant.product_template_attribute_value_ids:
            for attribute_line in variant.product_template_attribute_value_ids:
                attr_name, attr_id = self.update_woocommerce_attribute(
                    woocommerce, channel, attribute_line.attribute_id,attribute_line.product_attribute_value_id)
                value_name = attribute_line.product_attribute_value_id.name
                attribute_dict.append({
                    'id'	: attr_id,
                    'name'	: attr_name,
                    'option': value_name,
                })
        return attribute_dict

    def update_woocommerce_attribute_value(self, attribute_line):
        value_list = []
        if attribute_line:
            for value in attribute_line.value_ids:
                value_list.append(value.name)
        return value_list

    def update_woocommerce_attribute(self, woocommerce, channel, attribute_id,attribute_value_ids):
        if attribute_id:
            vals_list = [attribute_id.name,""]
            updated = self.env['export.woocommerce.attributes'].with_context({
                "channel_id": channel,
                "woocommerce": woocommerce,
            }).export_attribute(attribute_id,attribute_value_ids)
            if updated[0]:
                    vals_list[1] = updated[1]
            return vals_list

    def update_woocommerce_attribute_line(self, woocommerce, channel, template):
        attribute_list = []
        attribute_count = 0
        if template.attribute_line_ids:
            for attribute_line in template.attribute_line_ids:
                attr_name, attr_id = self.update_woocommerce_attribute(
                    woocommerce, channel, attribute_line.attribute_id,attribute_line.value_ids)
                values = self.update_woocommerce_attribute_value(attribute_line)
                attribute_dict = {
                    'name'		: attr_name,
                    'id'		: attr_id,
                    'variation'	: True,
                    'visible'	: True,
                    'position'	: attribute_count,
                    'options'	: values,
                }
                attribute_count += 1
                attribute_list.append(attribute_dict)
        return attribute_list

    def update_woocommerce_variation(self, woocommerce, channel, store_template_id, template, image_ids=False):
        count = 0
        variant_list = []
        if store_template_id and template:
            for variant in template.product_variant_ids:
                match_record = self.env['channel.product.mappings'].search([
                    ('product_name', '=', variant.id),
                    ('channel_id', '=', channel.id)])
                if match_record:
                    quantity = channel.get_quantity(variant)
                    variant_data = {
                        'regular_price'	: str(variant.price) or "",
                        'visible'		: True,
                        'sku'			: variant.default_code or "",
                        'stock_quantity': quantity,
                        'description'	: variant.description or "",
                        'price'			: str(variant.price),
                        'manage_stock'	: True,
                        'in_stock'		: True,
                        'attributes'	: self.update_woocommerce_attribute_dict(woocommerce, channel, variant),
                    }
                    if variant.length or variant.width or variant.height:
                        dimensions = {
                            'width': str(variant.width) or "",
                            'length': str(variant.length) or "",
                            'unit': str(variant.dimensions_uom_id.name) or "",
                            'height': str(variant.height) or "",
                        }
                        variant_data['dimensions'] = dimensions
                    if variant.weight:
                        variant_data['weight'] = str(variant.weight) or ""
                    if image_ids:
                        variant_data.update(
                            {'image': {'id': image_ids[count]}})
                    return_dict = woocommerce.put("products/"+str(store_template_id)+"/variations/"+str(
                        match_record.store_variant_id), variant_data).json()
                    if "message" in return_dict:
                        _logger.info("Error in updating Variants ===> %r",return_dict["message"])
                        continue
                    count += 1
                    variant_list.append(return_dict['id'])
                else:
                    _logger.info(
                        '<<<<<<<<<<< Product not updated to Woocommerce. >>>>>>>>>>')
            return variant_list
        else:
            raise UserError(
                _('Error in updating Product Variant with id (%s)' % variant.id))

    def update_woocommerce_variable_product(self, woocommerce, channel, template, remote_id):
        if template:
            product_dict = {
                'name'				: template.name,
                'sku' 				: "",
                'images'			: self.update_woocommerce_product_image(template,True),
                'type'				: 'variable',
                'categories'		: self.set_woocommerce_product_categories(woocommerce, channel, template),
                'status'			: 'publish',
                'manage_stock'		: False,
                'attributes'		: self.update_woocommerce_attribute_line(woocommerce, channel, template),
                'default_attributes': self.update_woocommerce_attribute_dict(woocommerce, channel, template.product_variant_ids[0]),
                'short_description'	: template.description_sale or "",
                'description'		: template.description or "",
            }
            if template.length or template.width or template.height:
                dimensions = {
                    u'width': str(template.width) or "",
                    u'length': str(template.length) or "",
                    u'unit': str(template.dimensions_uom_id.name) or "",
                    u'height': str(template.height) or "",
                }
                product_dict['dimensions'] = dimensions
            if template.weight:
                product_dict['weight'] = str(template.weight) or ""
            if woocommerce:
                url = 'products/%s' % remote_id
                return_dict = woocommerce.put(url, product_dict).json()
                image_ids = []
                if 'images' in return_dict:
                    for image in return_dict['images']:
                        if image['position'] != 0:
                            image_ids.append(image['id'])
                if 'id' in return_dict:
                    store_template_id = return_dict['id']
                    if image_ids:
                        return_list = self.update_woocommerce_variation(
                            woocommerce, channel, remote_id, template, image_ids=image_ids)
                    else:
                        return_list = self.update_woocommerce_variation(
                            woocommerce, channel, remote_id, template)
                    if len(return_list):
                        return (store_template_id, return_list)
                else:
                    raise UserError(
                        _("Error in Updating Product Template in Woocommerce."))

    def update_woocommerce_simple_product(self, woocommerce, channel, template, remote_id):
        quantity = channel.get_quantity(template)
        product_dict = {
            'name'				: template.name,
            'sku' 				: template.default_code or "",
            'regular_price'		: str(template.with_context(pricelist=channel.pricelist_name.id).price) or "",
            'type'				: 'simple',
            'categories'		: self.set_woocommerce_product_categories(woocommerce, channel, template),
            'status'			: 'publish',
            'short_description'	: template.description_sale or "",
            'description'		: template.description or "",
            'attributes'		: self.update_woocommerce_attribute_line(woocommerce, channel, template),
            'price'				: template.with_context(pricelist=channel.pricelist_name.id).price,
            'manage_stock'		: True,
            'stock_quantity'	: quantity,
            'in_stock'			: True,
        }
        # if template.image_1920:
        # 	product_dict['images'] = self.update_woocommerce_product_image(template)
        if template.length or template.width or template.height:
            dimensions = {
                'width': str(template.width) or "",
                'length': str(template.length) or "",
                'unit': str(template.dimensions_uom_id.name) or "",
                'height': str(template.height) or "",
            }
            product_dict['dimensions'] = dimensions
        if template.weight:
            product_dict['weight'] = str(template.weight)
        if woocommerce:
            url = 'products/%s' % remote_id
            return_dict = woocommerce.put(url, product_dict).json()
        if 'id' in return_dict:
            return return_dict['id']
        else:
            raise UserError(_('Simple Product Updation Failed'))

    def set_woocommerce_product_categories(self, woocommerce, channel, template):
        categ_list = []
        if template.categ_id:
            cat_id = self.export_woocommerce_categories_id(
                woocommerce, channel, template.categ_id)
            if cat_id:
                categ_list.append({'id': cat_id})
        if template.channel_category_ids:
            for category_channel in template.channel_category_ids:
                if category_channel.instance_id.id == channel.id:
                    for category_id in category_channel.extra_category_ids:
                        extra_categ_id = self.update_woocommerce_categories_id(
                            woocommerce, channel, category_id)
                        categ_list.append({'id': extra_categ_id})
        return categ_list
    
    def update_woocommerce_categories_id(self, woocommerce, channel, cat_record):
        store_cat_id = None
        is_cat_mapped = self.env['channel.category.mappings'].search([
            ('channel_id', '=', channel.id),
            ("odoo_category_id", '=', cat_record.id)
        ])
        if not is_cat_mapped:
            remote_object = self.env['export.categories'].create({
                "channel_id": channel.id,
                "operation": 'export',
            }).with_context({
                "channel_id": channel,
                "woocommerce": woocommerce,
                "with_product":True
                }).woocommerce_export_now(cat_record, cat_record.id)
            if remote_object[0]:
                store_cat_id = remote_object[1].id
                _logger.info(
                    "Product Category Exported with ID (%r)", cat_record.id)
        else:
            store_cat_id = is_cat_mapped.store_category_id
        return store_cat_id