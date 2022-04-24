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


class UpdateWoocommerceCategories(models.TransientModel):
    _inherit = "export.categories"

    def woocommerce_update_now(self, record, initial_record_id, remoteid):
        return_list = [False, '']
        odoo_category_id = record.id
        channel = self._context.get('channel_id')
        woocommerce = self._context.get('woocommerce')
        is_cat_mapped = self.env['channel.category.mappings'].search([
            ('channel_id', '=', channel.id),
            ('odoo_category_id', '=', odoo_category_id)])
        if is_cat_mapped.need_sync == 'yes':
            remote_id = is_cat_mapped.store_category_id
            remote_object = self.woocommerce_sync_categories_update(
                channel, woocommerce, record, initial_record_id, remote_id)
            return_list = [True, remote_object]
        return return_list

    def woocommerce_sync_categories_update(self, channel, woocommerce, record, initial_record_id, remote_id, ):
        p_cat_id = 0
        res = ''
        if record.parent_id.id:
            is_parent_mapped = self.env['channel.category.mappings'].search([
                ("channel_id", '=', channel.id),
                ('odoo_category_id', '=', record.parent_id.id)])
            if is_parent_mapped:
                p_cat_id = self.with_context({
                    'channel_id': channel,
                    'woocommerce': woocommerce,
                }).woocommerce_update_now(record.parent_id, initial_record_id)
            else:
                p_cat_id = self.env['export.categories'].create({
                    "channel_id": channel.id,
                    "operation": "export"
                }).with_context({
                    'channel_id': channel,
                    'woocommerce': woocommerce,
                }).woocommerce_export_now(record.parent_id, initial_record_id)
            if isinstance(p_cat_id, list):
                p_cat_id = p_cat_id[1].id
        res = self.woocommerce_update_category(
            woocommerce, channel, record, initial_record_id, p_cat_id, remote_id)
        return res

    def woocommerce_update_category(self, woocommerce, channel, record, initial_record_id, p_cat_id, remote_id):
        returnid = None
        category_dict = {
            "name": record.name,
            "parent": p_cat_id,
        }
        return_dict = woocommerce.put(
            'products/categories/%s' % remote_id, category_dict).json()
        if 'message' in return_dict:
            raise UserError('Error in Updating Categories : ' +
                            str(return_dict['message']))
        returnid = return_dict.get("id")
        if record.id != initial_record_id :
            channel.create_category_mapping(record,returnid)
        return returnid