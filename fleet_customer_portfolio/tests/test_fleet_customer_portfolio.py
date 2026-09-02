from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFleetCustomerPortfolio(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portfolio = cls.env["fleet.customer.portfolio"]

    def _new_customer(self, name="Portfolio Test Customer", **values):
        return self.env["res.partner"].create({'name': name, 'es_cliente': True, **values})

    def test_only_flagged_partners_are_in_the_portfolio(self):
        included = self._new_customer()
        excluded = self.env["res.partner"].create({'name': "Not A Portfolio Customer"})

        ids = [c['id'] for c in self._all_rows()]

        self.assertIn(included.id, ids)
        self.assertNotIn(excluded.id, ids)

    def _all_rows(self):
        rows, offset = [], 0
        while True:
            page = self.portfolio.get_dashboard_data(offset=offset, limit=200)
            rows += page['clients']
            offset += page['limit']
            if offset >= page['total']:
                return rows

    def test_search_matches_name(self):
        customer = self._new_customer(name="Zzz Unrepeatable Portfolio Name")

        data = self.portfolio.get_dashboard_data(search="Unrepeatable Portfolio")

        self.assertEqual([c['id'] for c in data['clients']], [customer.id])
        self.assertEqual(data['total'], 1)

    def test_paging_walks_the_whole_set_without_repeats(self):
        first = self.portfolio.get_dashboard_data(offset=0, limit=5)
        second = self.portfolio.get_dashboard_data(offset=5, limit=5)

        self.assertEqual(len(first['clients']), 5)
        self.assertFalse(
            {c['id'] for c in first['clients']} & {c['id'] for c in second['clients']},
            "a page must not repeat rows from the previous one",
        )

    def test_total_counts_the_whole_set_not_the_page(self):
        data = self.portfolio.get_dashboard_data(offset=0, limit=1)

        self.assertEqual(len(data['clients']), 1)
        self.assertEqual(
            data['total'],
            self.env["res.partner"].search_count([('es_cliente', '=', True)]),
        )

    def test_policy_tone_follows_the_policy_state(self):
        # fleet.poliza cannot be built here: both cliente_id and estado_vigencia
        # are stored computes fed by the vehicle and its attachment.
        tones = {state: self.portfolio._policy_display(state)['tone']
                 for state in ('vigente', 'falta_subir', 'vencido')}

        self.assertEqual(tones, {'vigente': 'green', 'falta_subir': 'amber', 'vencido': 'red'})
        self.assertEqual(self.portfolio._policy_display(None)['tone'], 'grey')

    def test_risk_level_escalates_on_the_worst_signal(self):
        self.assertEqual(self.portfolio._risk_level('vencido', 0, 'on_time'), 'red')
        self.assertEqual(self.portfolio._risk_level('vigente', 0, 'breached'), 'red')
        self.assertEqual(self.portfolio._risk_level('vigente', 1, 'on_time'), 'amber')
        self.assertEqual(self.portfolio._risk_level('falta_subir', 0, 'on_time'), 'amber')
        self.assertEqual(self.portfolio._risk_level('vigente', 0, 'on_time'), 'green')

    def test_customer_without_sources_is_green(self):
        row = self._row_for(self._new_customer())

        self.assertEqual(row['risk_level'], 'green')

    def test_unwired_blocks_report_themselves_as_pending(self):
        row = self._row_for(self._new_customer())

        for block in ('collection', 'documents'):
            self.assertEqual(row[block]['label'], "—")
            self.assertTrue(row[block]['pending'], "a pending block must say what it waits for")

    def test_arrears_outrank_a_payment_plan(self):
        overdue_on_plan = {'days': 12, 'plans': 1, 'due': 1060.0, 'next_charge': None}
        on_plan = {'days': 0, 'plans': 1, 'due': 0.0, 'next_charge': None}
        clean = {'days': 0, 'plans': 0, 'due': 0.0, 'next_charge': None}

        self.assertEqual(self.portfolio._collection_display(overdue_on_plan)['tone'], 'red')
        self.assertEqual(self.portfolio._collection_display(on_plan)['tone'], 'amber')
        self.assertEqual(self.portfolio._collection_display(clean)['tone'], 'green')
        self.assertEqual(self.portfolio._collection_display(None)['tone'], 'grey')

    def test_days_overdue_turn_the_row_red(self):
        overdue = {'days': 1, 'plans': 0, 'due': 10.0, 'next_charge': None}

        self.assertEqual(self.portfolio._risk_level('vigente', 0, 'on_time', overdue), 'red')
        self.assertEqual(self.portfolio._risk_level('vigente', 0, 'on_time', None), 'green')

    def test_arrears_filter_only_returns_customers_with_days_overdue(self):
        data = self.portfolio.get_dashboard_data(quick_filter='arrears', limit=200)

        self.assertEqual(data['total'], data['kpis']['in_arrears'])
        for client in data['clients']:
            self.assertEqual(client['collection']['tone'], 'red')

    def test_quick_filter_narrows_to_customers_with_a_claim(self):
        customer = self._new_customer()
        self.env["fleet.siniestro"].create({'cliente_id': customer.id})

        data = self.portfolio.get_dashboard_data(quick_filter='claim')

        self.assertIn(customer.id, [c['id'] for c in data['clients']])
        self.assertTrue(all(c['claim_count'] for c in data['clients']))

    def test_current_contracts_come_before_the_rest(self):
        contracts = self.env["fleet.vehicle.log.contract"].with_context(active_test=False)
        partner = contracts.search([('cliente_id', '!=', False)], limit=1).cliente_id
        if not partner:
            self.skipTest("no contract is linked to a customer in this database")

        cards = self.portfolio.get_client_detail(partner.id)['contracts']

        seen_closed = False
        for card in cards:
            if card['status_tone'] != 'green':
                seen_closed = True
            elif seen_closed:
                self.fail("a current contract must not follow a closed one")

    def test_each_contract_carries_its_own_semaphore(self):
        contracts = self.env["fleet.vehicle.log.contract"].with_context(active_test=False)
        partner = contracts.search([('cliente_id', '!=', False)], limit=1).cliente_id
        if not partner:
            self.skipTest("no contract is linked to a customer in this database")

        labels = self.portfolio._indicator_labels()
        for card in self.portfolio.get_client_detail(partner.id)['contracts']:
            self.assertEqual(sorted(i['key'] for i in card['indicators']), sorted(labels))

    def test_customer_without_contracts_still_gets_a_band(self):
        detail = self.portfolio.get_client_detail(self._new_customer().id)

        self.assertFalse(detail['has_contracts'])
        self.assertEqual(len(detail['contracts']), 1)
        self.assertEqual(detail['contracts'][0]['id'], 0)
        keys = [i['key'] for i in detail['contracts'][0]['indicators']]
        self.assertEqual(sorted(keys), sorted(self.portfolio._indicator_labels()))

    def test_every_card_carries_the_keys_the_sheet_renders(self):
        contracts = self.env["fleet.vehicle.log.contract"].with_context(active_test=False)
        partner = contracts.search([('cliente_id', '!=', False)], limit=1).cliente_id
        if not partner:
            self.skipTest("no contract is linked to a customer in this database")

        card = self.portfolio.get_client_detail(partner.id)['contracts'][0]

        for block in ('details', 'collection', 'tickets', 'claim', 'documents'):
            self.assertIn(block, card)
        self.assertIn('progress_pct', card['details'])
        self.assertIn('items', card['documents'])
        self.assertIn('source', card['claim'])

    def test_facts_without_a_source_say_so(self):
        contracts = self.env["fleet.vehicle.log.contract"].with_context(active_test=False)
        partner = contracts.search([('cliente_id', '!=', False)], limit=1).cliente_id
        if not partner:
            self.skipTest("no contract is linked to a customer in this database")

        card = self.portfolio.get_client_detail(partner.id)['contracts'][0]

        self.assertEqual(card['details']['deposit'], "—")
        self.assertIn("—", [row['value'] for row in card['operations']])

    def test_the_salesperson_is_the_latest_delivery_advisor(self):
        """agenda.entrega has no link to the contract, so the vehicle is the
        join and the newest delivery wins: a unit leased again is delivered
        again, and the sheet is about the current lease."""
        delivery = self.env["agenda.entrega"].search(
            [('asesor_id', '!=', False)], order='id desc', limit=1)
        if not delivery:
            self.skipTest("no delivery carries an advisor in this database")

        self.assertEqual(self.portfolio._delivery_advisor(delivery.vehiculo_id),
                         delivery.asesor_id.name)
        self.assertIsNone(self.portfolio._delivery_advisor(self.env["fleet.vehicle"]))

    def test_every_customer_gets_an_interaction_block(self):
        """A None here crashed the whole 360 on any customer with no log."""
        for partner in (self._new_customer(),
                        self.env["res.partner"].search([('es_cliente', '=', True)], limit=3)):
            for one in partner:
                block = self.portfolio.get_client_detail(one.id)['interaction']
                self.assertIsNotNone(block)
                self.assertIn('items', block)

    def test_collection_entries_are_capped(self):
        from odoo.addons.fleet_customer_portfolio.models.fleet_customer_portfolio import (
            COLLECTION_ENTRIES_SHOWN,
        )
        credits = self.env["credito.arrendamiento"].search([])
        for credit in credits:
            entries = self.portfolio._collection_entries(credit)
            self.assertLessEqual(len(entries), COLLECTION_ENTRIES_SHOWN)
            self.assertFalse([e for e in entries if 'due' in e],
                             "the sorting key must not leak into the payload")

    def _row_for(self, partner):
        data = self.portfolio.get_dashboard_data(search=partner.name)
        rows = [c for c in data['clients'] if c['id'] == partner.id]
        self.assertTrue(rows, "the customer should be in its own search results")
        return rows[0]
