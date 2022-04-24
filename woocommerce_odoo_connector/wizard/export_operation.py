from ..ApiTransaction import WoocommerceTransaction
from odoo import models, fields, exceptions

class WoocommerceExportOperation(models.TransientModel):
    _inherit = "export.operation"

    def export_button(self):
        if self._context.get('active_model','multi.channel.sale') == 'multi.channel.sale':
            return WoocommerceTransaction(channel=self.channel_id).woocommerce_export_data(
                object = self.object,
                object_ids = self.env[self.object].search([]).ids,
                operation = 'export',
            )
        else:
            return WoocommerceTransaction(channel=self.channel_id).woocommerce_export_data(
                object = self._context.get('active_model'),
                object_ids = self._context.get('active_ids'),
                operation = self.operation,
            )
