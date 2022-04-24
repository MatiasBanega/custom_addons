# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H#########Y#########P#########N#########O##########S##################

import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Importwoocommercepartners(models.TransientModel):
    _name = "import.woocommerce.partners"
    _inherit = 'import.partners'
    _description = "Import Woocommerce Partners"

    def import_now(self, **kwargs):
        data_list = []
        woocommerce = self._context.get('woocommerce')
        customer_id = kwargs.get('woocommerce_object_id')
        if customer_id:
            data_list = self.get_customer_by_id(woocommerce, customer_id)
        elif kwargs.get("woocommerce_import_date_from"):
            data_list, last_added = self._filter_customer_using_date(woocommerce, **kwargs)
            kwargs["last_added"] = last_added
        else:
            data_list = self.get_customer_all(woocommerce, **kwargs)
        return data_list, kwargs
    
    def _filter_customer_using_date(self, woocommerce, **kwargs):
        if woocommerce:
            vals_list = []
            date_created = None
            import_date_from = kwargs.get("woocommerce_import_date_from")
            import_date_from = import_date_from.isoformat()
            page_number =kwargs.get("page_number")
            page_size = kwargs.get("page_size")
            url = 'customers?after={}&page={}&per_page={}'.format(import_date_from, str(page_number),page_size)
            partner_data = woocommerce.get(url).json()
            if "message" in partner_data:
                _logger.info("Error in Importing Customers : %r",partner_data["message"])
                if not kwargs.get("from_cron"):
                    raise UserError("Error in Importing Customers : {}".format(partner_data["message"]))
            if partner_data:
                for data in partner_data:
                    vals_list.append(self.get_contact_address(data))
                date_created = partner_data[-1].get("date_created")
            return vals_list, date_created

    def get_customer_all(self, woocommerce, **kwargs):
        vals_list = []
        page_number = kwargs.get("page_number")
        page_size = kwargs.get("page_size")
        url = 'customers?page={}&per_page={}'.format(str(page_number),page_size)
        partner_data = woocommerce.get(url).json()
        if "message" in partner_data:
            _logger.info("Error in Importing Customers : %r",partner_data["message"])
            raise UserError("Error in Importing Customers : {}".format(str(partner_data["message"])))
        if partner_data:
            for data in partner_data:
                vals_list.append(self.get_contact_address(data))
        return vals_list

    def get_contact_address(self, data):
        if data:
            return {
                "channel_id": self.channel_id.id,
                "channel": self.channel_id.channel,
                "store_id": data.get("id"),
                "name": data.get('first_name'),
                "last_name": data.get("last_name"),
                "type": "contact",
                "email": data.get("email") or "",
                "street": data['billing'].get("address_1") or "",
                "street2": data['billing'].get("address_2") or "",
                "zip": data['billing'].get("postcode") or "",
                "city": data['billing'].get("city") or "",
                # "state_name":state_data.get("state_name"),
                "state_code": data['billing'].get("state") or "",
                "country_code": data['billing'].get('country') or "",
                "phone":data["billing"].get("phone") or ""
            }

    def get_customer_by_id(self, woocommerce, customer_id):
        vals_list = []
        url = 'customers/%s' % customer_id
        partner_data = woocommerce.get(url).json()
        if "message" in partner_data:
            _logger.info("Error in Importing Customers : %r",partner_data["message"])
            raise UserError("Error in Importing Customers : {}".format(str(partner_data["message"])))
        if partner_data:
            vals_list.append(self.get_contact_address(partner_data))
        return vals_list