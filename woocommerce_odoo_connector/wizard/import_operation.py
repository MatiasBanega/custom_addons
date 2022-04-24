# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H#########Y#########P#########N#########O#########S###################
from odoo import api, fields, models, exceptions
from ..ApiTransaction import WoocommerceTransaction


class WoocommerceImportOperation(models.TransientModel):
    _inherit = "import.operation"

    woocommerce_object_id = fields.Char()
    woocommerce_import_date_from = fields.Datetime()
    woocommerce_filter_type = fields.Selection(
        [('all', 'All'), ("by_id", "By Id"), ("by_date", "By Date")], default='all')

    def woocommerce_get_filter(self):
        return dict(
            woocommerce_object_id=self.woocommerce_object_id,
            woocommerce_import_date_from=self.woocommerce_import_date_from,
            page_size = self.channel_id.api_record_limit,
            page_number = 1
        )

    def import_with_filter(self, **kw):
        if self.channel_id.channel == "woocommerce":
            return WoocommerceTransaction(channel=self.channel_id).woocommerce_import_data(**kw)
        else:
            return super(WoocommerceImportOperation,self).import_with_filter(**kw)