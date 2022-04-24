# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H#########Y#########P#########N#########O#########S###################
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError

class ImportWoocommerceAttributes(models.TransientModel):
    _name = "import.woocommerce.attributes"
    _inherit = "import.operation"
    _description = "Import Woocommerce Attributes "

    def import_woocommerce_attribute(self):
        woocommerce = self._context.get('woocommerce')
        channel = self._context.get('channel_id')
        odoo_attribute_id = 0
        i = 1
        while (i):
            try:
                attribute_data = woocommerce.get('products/attributes?page='+str(i)).json()
            except Exception as e:
                raise UserError(_("Error : "+str(e)))
            if 'message' in attribute_data:
                raise UserError(_("Error : "+str(attribute_data['message'])))
            else:
                if attribute_data:
                    i = i+1
                    product_attributes_obj = self.env['product.attribute']
                    for attribute in attribute_data:
                        attribute_id =  attribute['id']
                        attribute_map = self.env['channel.attribute.mappings'].search([
                            ('store_attribute_id', '=', attribute_id),
                            ('channel_id', '=', channel.id)])
                        attribute_search_record = product_attributes_obj.search([
                                '|', ('name', '=', attribute['name']),
                                '|', ('name', '=', attribute['name'].lower()),
                                '|', ('name', '=', attribute['name'].title()),
                                ('name', '=', attribute['name'].upper())])
                        if not attribute_search_record:
                            odoo_attribute_id = product_attributes_obj.create(
                                {'name': attribute['name']})
                        else:
                            odoo_attribute_id = attribute_search_record
                        if not attribute_map:
                            mapping_dict = {
                                'channel_id': channel.id,
                                "ecom_store": channel.channel,
                                'store_attribute_id': attribute_id,
                                'store_attribute_name': attribute['name'],
                                'odoo_attribute_id': odoo_attribute_id.id,
                                'attribute_name': odoo_attribute_id.id,
                            }
                            obj = self.env['channel.attribute.mappings']
                            channel._create_mapping(obj, mapping_dict)
                        attr_term = self.import_woocommerce_attribute_terms(
                                        channel, woocommerce, attribute_id, odoo_attribute_id)
                    else:
                        i = 0
                self._cr.commit()
                return True

    def import_woocommerce_attribute_terms(self, channel, woocommerce, store_attribute_id,odoo_attribute_id):
        if not woocommerce:
            woocommerce = self.get_woocommerce_connection()
        odoo_attribute_value_id = 0
        i =1
        while(i):
            try:
                attribute_term_data = woocommerce.get(
                        'products/attributes/'+str(store_attribute_id)+'/terms').json()
            except Exception as e:
                _logger.info("Error -> %r",str(e))
            if "message" in attribute_term_data:
                _logger.info("Error:- >%r",str(attribute_term_data['message']))
            else:
                if attribute_term_data:
                        i = i+1
                        for term in attribute_term_data:
                            term_map = self.env['channel.attribute.value.mappings'].search(
                                [('store_attribute_value_id', '=', term['id']), ('channel_id', '=', channel.id)],limit=1)
                            if not term_map:
                                product_attributes_value_obj = self.env['product.attribute.value']
                                attribute_value_search_record = product_attributes_value_obj.search([
                                    ('attribute_id', '=', odoo_attribute_id.id),
                                    '|', ('name', '=', term['name']),
                                    '|', ('name', '=', term['name'].lower(
                                    )),
                                    '|', ('name', '=', term['name'].title(
                                    )),
                                    ('name', '=', term['name'].upper())
                                ])
                                if not attribute_value_search_record:
                                    _logger.info("odoo attribute id ========> %r",odoo_attribute_id)
                                    odoo_attribute_value_id = product_attributes_value_obj.create(
                                        {'name': term['name'], 'attribute_id': odoo_attribute_id.id})
                                else:
                                    odoo_attribute_value_id = attribute_value_search_record
                                mapping_dict = {
                                    'channel_id': channel.id,
                                    'store_attribute_value_id': term['id'],
                                    'store_attribute_value_name': term['name'],
                                    'odoo_attribute_value_id': odoo_attribute_value_id.id,
                                    'attribute_value_name': odoo_attribute_value_id.id,
                                    'ecom_store': channel.channel,
                                }
                                obj = self.env['channel.attribute.value.mappings']
                                channel._create_mapping(obj, mapping_dict)
                        else:
                            i = 0
        return True