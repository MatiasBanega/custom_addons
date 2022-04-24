# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H#########Y#########P#########N#########O#########S###################

from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import api, fields, models
from odoo.tools.translate import _

class ImportWoocommerceCategories(models.TransientModel):
    _name = "import.woocommerce.categories"
    _inherit = 'import.categories'
    _description = "Import Woocommerce Categories"

    def get_category_all(self, woocommerce, page_number,page_size):
        vals_list = []
        cat_url = 'products/categories?page={}&per_page={}'.format(page_number,page_size)
        category_data = woocommerce.get(cat_url).json()
        if "message" in category_data:
            error_message = "Error in getting Category data:- {}".format(category_data["message"])
            _logger.info(error_message)
            raise UserError(error_message)
        if category_data:
            vals_list = list(map(lambda x: self.get_category_vals(x),category_data))
        return vals_list

    def get_category_by_id(self, woocommerce, category_id):
        vals_list = []
        parent_data  = None
        cat_url = "products/categories/%s" % category_id
        category_data = woocommerce.get(cat_url).json()
        if "message" in category_data:
            error_message = "Error in getting Category data:- {}".format(category_data["message"])
            _logger.info(error_message)
            raise UserError(error_message)
        if category_data:
            parent_id = category_data.get("parent")
            if parent_id:
                parent_data = self.get_category_by_id(woocommerce, parent_id)
                vals_list += parent_data
            data = self.get_category_vals(category_data)
            vals_list.append(data)
            return vals_list
    
    def get_category_vals(self, category_data):
        if category_data:
            parent_id = category_data.get("parent")
            vals =  {
                            "channel_id": self.channel_id.id,
                            "channel": self.channel_id.channel,
                            "leaf_category": True if parent_id else False,
                            "store_id": category_data.get("id"),
                            "name": category_data.get("name"),
                        }
            if parent_id != 0:
                vals["parent_id"] = parent_id
            return vals

    def import_now(self,**kwargs):
        data_list = []
        woocommerce = self._context.get('woocommerce')
        woocommerce_object_id = kwargs.get('woocommerce_object_id')
        page_number = kwargs.get("page_number")
        page_size = kwargs.get("page_size")
        if woocommerce_object_id:
            data_list = self.get_category_by_id(woocommerce, woocommerce_object_id)
        else:
            data_list = self.get_category_all(woocommerce, page_number, page_size)
        return data_list, kwargs