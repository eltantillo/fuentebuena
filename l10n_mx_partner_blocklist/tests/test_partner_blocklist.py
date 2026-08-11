import requests_mock

from odoo.exceptions import ValidationError
from odoo.tests import Form, tagged

from odoo.addons.l10n_mx_edi.tests.common import TestMxEdiCommon


@tagged("post_install", "-at_install")
class TestL10nMxPartnerBlocklist(TestMxEdiCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_camptocamp = cls.env.ref("base.res_partner_12")
        cls.partner_camptocamp.write({"l10n_mx_in_blocklist": "normal"})
        cls.server_action = cls.env.ref("l10n_mx_partner_blocklist.partner_blocklist_status_server_action")
        cls.partner_blacklist = cls.env["res.partner.blacklist"]
        cls.url = cls.env["ir.config_parameter"].sudo().get_param("l10n_mx_partner_blocklist_url")

    def test_partner_blocklist(self):
        # Get the number of records existing in the downloaded CSV file
        mock_csv_content = (
            "HEADER1\n"
            "HEADER2\n"
            "No.,RFC,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20,C21,C22,\n"
            '1,XAXX010101001,"Test company S.A. de C.V.",Definitivo,'
            "500-05-2016-38728 de fecha 16 de diciembre de 2016,01/01/2017,"
            "500-05-2016-38728 de fecha 16 de diciembre de 2016,19/01/2017,,,,,"
            "500-05-2018-14172 de fecha 25 de mayo de 2018,25/05/2018,"
            "500-05-2018-14172 de fecha 25 de mayo de 2018,28/06/2018,,,,,,,"
        )
        with requests_mock.mock() as mock:
            mock.get(self.url, text=mock_csv_content)
            count_blacklist_downloaded = self.partner_blacklist.download_csv_partner_list()
            # Get the number of records inserted into the res_partner_blacklist table
            count_blacklist_inserted = self.partner_blacklist.search_count([])
            # Validate that the number of records matches the number of inserted records.
            self.assertEqual(
                count_blacklist_downloaded,
                count_blacklist_inserted,
                (
                    "The number of records downloaded does not match the number of "
                    "records inserted into the res_partner_blacklist table"
                ),
            )

        # Checking partner status messages
        self.assertEqual(self.partner_camptocamp.l10n_mx_in_blocklist, "done", "The action was already executed")
        self.partner_camptocamp.write(
            {
                "vat": "XAXX010101000",
            }
        )
        self.server_action.with_context(
            **{"active_ids": self.partner_camptocamp.id, "active_model": "res.partner"}
        ).run()
        self.assertEqual(self.partner_camptocamp.l10n_mx_in_blocklist, "done", "The partner is not OK")
        self.env["res.partner.blacklist"].sudo().create(
            {
                "vat": "XAXX010101000",
                "taxpayer_name": self.partner_camptocamp.name,
            }
        )
        self.server_action.with_context(
            **{"active_ids": self.partner_camptocamp.id, "active_model": "res.partner"}
        ).run()
        self.assertEqual(self.partner_camptocamp.l10n_mx_in_blocklist, "blocked", "The partner is not blocked")

        # Checking the user is not able to sale, purchase or invoicing with
        # a blocked partner.
        raise_msg = "The SAT provides a block list"

        try:
            self._create_invoice()
            self.assertEqual(self.partner_camptocamp.l10n_mx_in_blocklist, "blocked", "The Invoice has been validated")
        except ValidationError as e:
            self.assertEqual(raise_msg, e.name[:29])

    def test_warning_vat_change(self):
        """Test 'Partner SAT State' changes and warning displayed by the onchange method."""
        self.partner_blacklist.sudo().create(
            {
                "vat": "XAXX010101002",
                "taxpayer_name": self.partner_camptocamp.name,
            }
        )
        with Form(self.partner_camptocamp) as partner:
            self.assertEqual(partner.l10n_mx_in_blocklist, "normal", "The partner SAT state is not 'normal'.")
            partner.vat = "XAXX010101001"
            self.assertEqual(partner.l10n_mx_in_blocklist, "done", "The partner SAT state is not 'ok'.")
        self.partner_camptocamp.vat = "XAXX010101002"
        result = self.partner_camptocamp._onchange_l10n_mx_in_blocklist()
        self.assertEqual(
            self.partner_camptocamp.l10n_mx_in_blocklist, "blocked", "The partner SAT state is not 'blocked'."
        )
        self.assertIn("This partner appears in the SAT block list.", result.get("warning", {}).get("message", ""))
