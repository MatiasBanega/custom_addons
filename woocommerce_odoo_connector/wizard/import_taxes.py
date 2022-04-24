from odoo import models 
import logging
_logger = logging.getLogger(__name__)

class ImportWoocommerceTaxes(models.TransientModel):
    _inherit = "import.operation"
    _name = "import.woocommerce.taxes"
    _description  = "Import Woocommerce Taxes"

    def get_woocommerce_taxes(self, woocommerce, taxes, include_in_price):
        l = []
        if taxes:
            for tax in taxes:
                tax_id = tax.get("id")
                is_mapped = self.env["channel.account.mappings"].search([
                    ("channel_id","=",self.channel_id.id),
                    ("store_id","=",tax_id)
                    ])
                data = woocommerce.get(f"taxes/{tax_id}").json()
                if "message" in data :
                    _logger.info("Error in getting Taxes  %r",data["message"])
                    return l
                tax_rec = self.env["account.tax"].search([
                    ('name','=',data.get("name")),
                    ("amount","=",data.get("rate"))
                    ])
                vals = dict(        
                            amount=data.get("rate"),
                            name=data.get('name'),
                            amount_type = "percent"
                        )
                if not is_mapped:
                    if not tax_rec:
                        tax_created = self.env["account.tax"].create(vals)
                    tax_map_vals={
                                'channel_id'        : self.channel_id.id,
                                'tax_name'          : tax_rec.id,
                                'store_tax_value_id': str(tax_rec.amount),
                                'tax_type'          : tax_rec.amount_type,
                                'include_in_price'  : tax_rec.price_include,
                                'odoo_tax_id'       : tax_rec.id,
                                'store_id'          : tax_id,
                                }
                    self.channel_id._create_mapping(self.env["channel.account.mappings"],tax_map_vals)
                else:
                    is_mapped.tax_name.name = data.get("name")
                    is_mapped.tax_name.amount = data.get("rate")
                    is_mapped.store_tax_value_id = data.get("rate")
                l.append({"id":tax_id})
        return l
