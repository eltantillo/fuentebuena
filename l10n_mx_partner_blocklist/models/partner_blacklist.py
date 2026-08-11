import base64
import csv
import io
import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResPartnerBlacklist(models.Model):
    _name = "res.partner.blacklist"
    _description = "Partner Blacklist"
    _rec_name = "vat"

    number = fields.Char()
    vat = fields.Char(index=True, required=True)
    taxpayer_name = fields.Char(required=True)
    taxpayer_status = fields.Char(
        help="Taxpayer Status, if the status is set it means the taxpayer "
        "status is 'Definitivo' and this partner is not in a legal situation",
    )
    global_presumption = fields.Char(
        string="Presumption trade number and date",
    )
    sat_presumption = fields.Char(
        string="Presumption trade number and date from SAT",
    )
    sat_presumption_release = fields.Char(
        string="SAT date presumptions publication",
        help="This is the date when the SAT published in its website the " "presumed",
    )
    dof_presumption = fields.Char(
        string="Presumption trade number and date from DOF",
    )
    global_definitive = fields.Char(
        string="Definitive trade number and date",
    )
    sat_definitive_release = fields.Char(
        string="SAT date definitive publication",
        help="This is the date when the SAT published in its website the " "definitive",
    )
    dof_definitive_release = fields.Char(
        string="DOF date definitive publication",
        help="This is the date when the DOF published in its website the " "definitive",
    )

    def download_csv_partner_list(self):
        url = self.env["ir.config_parameter"].sudo().get_param("l10n_mx_partner_blocklist_url")
        if not url:
            _logger.warning("Partner blocklist URL is not configured.")
            return False
        _logger.info("Downloading partner blocklist from %s", url)
        file_name = "l10n_mx_partner_blocklist_res_partner_blacklist.csv"
        self.env["ir.attachment"].search([("name", "=", file_name)]).unlink()
        number_line = 0
        try:
            file_content, number_line = self.fetch_and_process_csv(url, number_line)
        except Exception:
            _logger.exception("Error downloading partner blocklist at line %s.", number_line)
            return 0
        if number_line:
            attachment_id = self.env["ir.attachment"].create(
                {
                    "name": file_name,
                    "datas": base64.encodebytes(file_content.encode("utf-8")),
                    "type": "binary",
                    "mimetype": "text/csv",
                    "description": "Partner Blocklist CSV",
                }
            )
            self.definitive_partner_list(attachment_id)
            attachment_id.unlink()
            self._update_partner_blocklist_status()
        return number_line

    def fetch_and_process_csv(self, url, number_line):
        file_content = ""
        list_file = requests.get(url, timeout=60)
        for count, line in enumerate(list_file.iter_lines()):
            # Ingore the header
            if not line or count <= 2:
                continue
            line = line.decode("utf-8", errors="ignore")
            reader = csv.reader([line], delimiter=",", quotechar='"')
            row = next(reader)
            # Remove additional double quotes
            row = [col.replace('""', '"') for col in row]
            # Select the required columns
            processed_row = row[0:8] + row[11:14]
            # Rebuild the line as standard CSV
            output = io.StringIO()
            writer = csv.writer(output, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(processed_row)
            file_content += output.getvalue()
            number_line += 1
        return file_content, number_line

    def definitive_partner_list(self, attachment_id):
        """Download CSV data from SAT and update data in Odoo database"""
        if not attachment_id:
            _logger.info(self.env._("Please check the blocklist attachment exists."))
            return False
        cr = self.env.cr
        cr.execute("DELETE FROM res_partner_blacklist;")
        cr.execute("DELETE FROM ir_model_data WHERE model='l10n_mx_partner_blocklist.res.partner.blacklist';")
        csv_path = attachment_id._full_path(attachment_id.store_fname)
        with open(csv_path, encoding="utf-8") as csv_file:
            cr.copy_expert(
                """COPY res_partner_blacklist(
                number, vat, taxpayer_name, taxpayer_status, global_presumption,
                sat_presumption, sat_presumption_release, dof_presumption,
                global_definitive, sat_definitive_release, dof_definitive_release)
                FROM STDIN WITH (FORMAT CSV, HEADER FALSE)""",
                csv_file,
            )
        # Create xml_id, to allow make reference to this data
        # Avoid save duplicated data
        try:
            cr.execute(
                """INSERT INTO ir_model_data
                (name, res_id, module, model, noupdate)
                SELECT concat('partner_code', vat), id,
                'l10n_mx_partner_blocklist',
                'l10n_mx_partner_blocklist.res.partner.blacklist', true
                FROM res_partner_blacklist
                ON CONFLICT (module, name) DO NOTHING"""
            )
        except Exception:
            _logger.exception("Error inserting ir.model.data for partner blacklist.")

    def _update_partner_blocklist_status(self, partners=None):
        """Bulk-update l10n_mx_in_blocklist on partners with a VAT.

        :param partners: Optional recordset of partners to update.
            When omitted, updates all partners that have a VAT.
        """
        blocked_vats = set(self.search([]).mapped("vat"))
        if partners is None:
            partners = self.env["res.partner"].with_context(active_test=False).search([("vat", "!=", False)])
        partners = partners.filtered("vat")
        to_block = partners.filtered(lambda p: p.vat in blocked_vats)
        to_ok = partners - to_block
        if to_block:
            to_block.write({"l10n_mx_in_blocklist": "blocked"})
        if to_ok:
            to_ok.write({"l10n_mx_in_blocklist": "done"})
