from odoo import models


import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _create_variant_ids(self):
        if self._context.get("skip_varient", False):
            return 
        return super(ProductTemplate, self)._create_variant_ids()