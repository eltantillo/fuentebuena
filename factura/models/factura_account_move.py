from odoo import fields,models,Command
import re
import logging
_logger = logging.getLogger(__name__)

class FacturaAccountMove(models.Model):
    _inherit = 'account.move.line'

    def _l10n_mx_edi_import_cfdi_fill_invoice_line(self, tree, line):
        # Product
        code = tree.attrib.get('NoIdentificacion')  # default_code if export from Odoo
        unspsc_code = tree.attrib.get('ClaveProdServ')  # UNSPSC code
        description = tree.attrib.get('Descripcion')  # label of the invoice line "[{p.default_code}] {p.name}"
        cleaned_name = re.sub(r"^\[.*\] ", "", description)
        product = self.env['product.product']._retrieve_product(
            name=cleaned_name,
            default_code=code,
            extra_domain=[('unspsc_code_id.code', '=', unspsc_code)],
            company=self.company_id,
        )
        codigo = self.env['product.unspsc.code'].search([('code', '=', unspsc_code)], limit=1)
        if not product:
            """product = self.env['product.product']._retrieve_product(name=cleaned_name, default_code=code)"""
            if codigo:
                categoria = self.env['product.unspsc.categoria'].search([('products_ids', 'in', codigo.id)], limit=1)
                if categoria and categoria.categoria_id:
                    # Buscar variante del producto.template si es necesario
                    product_variant = categoria.categoria_id.product_variant_id
                    if product_variant:
                        line.product_id = product_variant.id
                    else:
                        line.product_id = False
                else:
                    line.product_id = False
        # Taxes
        tax_ids = []
        for tax_node in tree.findall("{*}Impuestos/{*}Traslados/{*}Traslado"):
            tax = self._l10n_mx_edi_import_cfdi_get_tax_from_node(tax_node, line)
            if tax:
                tax_ids.append(tax.id)
        # Withholding Taxes
        for wh_tax_node in tree.findall("{*}Impuestos/{*}Retenciones/{*}Retencion"):
            wh_tax = self._l10n_mx_edi_import_cfdi_get_tax_from_node(wh_tax_node, line, is_withholding=True)
            if wh_tax:
                tax_ids.append(wh_tax.id)
        # Discount
        discount_percent = 0
        discount_amount = float(tree.attrib.get('Descuento') or 0)
        gross_price_subtotal_before_discount = float(tree.attrib.get('Importe'))
        if not self.currency_id.is_zero(discount_amount):
            discount_percent = (discount_amount/gross_price_subtotal_before_discount)*100
        line.write({
            'quantity': float(tree.attrib.get('Cantidad')),
            'price_unit': float(tree.attrib.get('ValorUnitario')),
            'discount': discount_percent,
            'tax_ids': [Command.set(tax_ids)],
            'descripcion': description,
            'codigo_id': codigo.id
        })
        return True