# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H#########Y#########P#########N#########O#########S###################
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.exceptions import UserError

class ExportWoocommerceAttributes(models.TransientModel):
    _name = 'export.woocommerce.attributes'
    _inherit = "export.operation"
    _description  = "Export Woocommerce Attributes"

    def export_attribute(self, attribute,attribute_values):
        woocommerce = self._context.get("woocommerce")
        channel = self._context.get("channel_id")
        vals_list = []
        is_attribute_mapped = self.env['channel.attribute.mappings'].search([
            ('odoo_attribute_id', '=', attribute.id),
            ('channel_id', '=', channel.id)])
        if not is_attribute_mapped:
            attribute_dict = {
                "name"			: attribute.name,
                "type"			: "select",
                "order_by"		: "menu_order",
                "has_archives"	: True
            }
            return_dict = woocommerce.post(
                'products/attributes', attribute_dict).json()
            if 'message' in return_dict:
                raise UserError('Error in Creating Attributes :' +
                                str(return_dict['message']))
            store_attribute_id = return_dict['id']
            mapping_dict = {
                'channel_id' : channel.id,
                'ecom_store' : channel.channel,
                'store_attribute_id' : store_attribute_id,
                'odoo_attribute_id' : attribute.id,
                'attribute_name' : attribute.id,
                'store_attribute_name' : attribute.name,
                'operation' : 'export'
            }
            obj = self.env['channel.attribute.mappings']
            channel._create_mapping(obj, mapping_dict)
        else:
            attribute_dict = {
                "name"			: attribute.name,
                "type"			: "select",
                "order_by"		: "menu_order",
                "has_archives"	: True
            }
            url = "products/attributes/%s" % (is_attribute_mapped.store_attribute_id)
            return_dict = woocommerce.put(
                url, attribute_dict).json()
            if 'message' in return_dict:
                raise UserError('Error in Updating Attributes :' +
                                str(return_dict['message']))
            store_attribute_id = is_attribute_mapped.store_attribute_id
        for attribute_value in attribute_values:
            vals = self.export_attribute_values(
                woocommerce, channel, attribute_value, store_attribute_id)
        _logger.info("Attribute with Id(%r) and its values %r are exported/updated to Woocommerce." % (
            attribute.id, vals))
        return [True, store_attribute_id]

    def export_attribute_values(self, woocommerce, channel, attribute_value, store_attribute_id):
        is_attribute_value_mapped = self.env['channel.attribute.value.mappings'].search([
            ("channel_id", '=', channel.id),
            ("attribute_value_name", '=', attribute_value.id)
        ])
        if not is_attribute_value_mapped:
            attribute_value_dict = {
                "name": attribute_value.name,
            }
            return_dict = woocommerce.post('products/attributes/' +
                                           str(store_attribute_id)+"/terms", attribute_value_dict).json()
            if 'message' in return_dict:
                raise UserError('Error in Creating terms ' +
                                str(return_dict['message']))
            mapping_dict = {
                'channel_id'				: channel.id,
                'ecom_store'					: channel.channel,
                'store_attribute_value_id'	: return_dict['id'],
                'odoo_attribute_value_id': attribute_value.id,
                'attribute_value_name'		: attribute_value.id,
                'store_attribute_value_name': attribute_value.name,
                'operation': 'export'
            }
            obj = self.env['channel.attribute.value.mappings']
            channel._create_mapping(obj, mapping_dict)
        else:
            attribute_value_dict = {
                "name": attribute_value.name,
            }
            url = "products/attributes/{}/terms/{}".format(store_attribute_id,is_attribute_value_mapped.store_attribute_value_id)
            return_dict = woocommerce.put(url, attribute_value_dict).json()
            if 'message' in return_dict:
                raise UserError('Error in Updating terms ' +
                                str(return_dict['message']))
          
        return attribute_value.id