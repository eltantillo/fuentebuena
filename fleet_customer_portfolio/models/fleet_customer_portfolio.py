from odoo import _, api, fields, models
from odoo.tools import format_date, formatLang

ROWS_PER_PAGE = 80

# An SLA deadline closer than this counts as at risk rather than on time.
SLA_RISK_HOURS = 24

OPEN_TICKET_DOMAIN = [('stage_id.fold', '=', False)]

# Tone of the chip on each contract card, by fleet.vehicle.log.contract.state.
CONTRACT_STATE_TONES = {
    'open': 'green',
    'futur': 'blue',
    'expired': 'amber',
    'closed': 'grey',
}

POLICY_SEVERITY = {'vigente': 0, 'falta_subir': 1, 'vencido': 2}

# Credit states that still say something about collection. A written-off or
# cancelled credit is history, not a signal on today's board.
LIVE_CREDIT_STATES = ('vigente',)

# How many collection movements the 360 sheet lists. They are picked by how
# close their due date is to today, so an agent on a call sees what is about to
# fall due instead of the whole schedule. Raise it and nothing else changes.
COLLECTION_ENTRIES_SHOWN = 5

# Both the amortization schedule and the payment-plan instalments use these.
INSTALMENT_TONES = {
    'pagada': 'green',
    'parcial': 'amber',
    'vencida': 'red',
    'pendiente': 'grey',
}


class FleetCustomerPortfolio(models.AbstractModel):
    """Read model behind the portfolio board and the 360 client sheet.

    Rows are `res.partner` records flagged `es_cliente`, the same set the
    "Clientes Pilotea" menu shows. Nothing is stored here: every figure is
    aggregated on demand from the modules that own it, and the blocks whose
    source is not wired yet report themselves as pending instead of guessing.
    """
    _name = 'fleet.customer.portfolio'
    _description = "Customer Portfolio"

    # -------------------------------------------------------------------------
    # DOMAINS
    # -------------------------------------------------------------------------
    @api.model
    def _customer_domain(self, search=None):
        domain = [('es_cliente', '=', True)]
        if search:
            domain += ['|', '|',
                       ('name', 'ilike', search),
                       ('vat', 'ilike', search),
                       ('id', 'in', list(self._partners_in_market(search)))]
        return domain

    @api.model
    def _partners_with_claims(self):
        return set(self.env['fleet.siniestro'].search([]).mapped('cliente_id').ids)

    @api.model
    def _partners_with_open_tickets(self):
        tickets = self.env['helpdesk.ticket'].search(OPEN_TICKET_DOMAIN)
        return set(tickets.mapped('partner_id').ids)

    @api.model
    def _partners_with_expired_policy(self):
        policies = self.env['fleet.poliza'].search([('estado_vigencia', '=', 'vencido')])
        return set(policies.mapped('cliente_id').ids)

    @api.model
    def _partners_in_arrears(self):
        credits = self.env['credito.arrendamiento'].search([
            ('estado', 'in', LIVE_CREDIT_STATES), ('dias_mora', '>', 0)])
        return set(credits.mapped('partner_id').ids)

    @api.model
    def _quick_filter_domain(self, quick_filter):
        if quick_filter == 'arrears':
            return [('id', 'in', list(self._partners_in_arrears()))]
        if quick_filter == 'claim':
            return [('id', 'in', list(self._partners_with_claims()))]
        if quick_filter == 'ticket':
            return [('id', 'in', list(self._partners_with_open_tickets()))]
        if quick_filter == 'policy':
            return [('id', 'in', list(self._partners_with_expired_policy()))]
        if quick_filter == 'documents':
            return [('id', 'in', list(self._partners_with_pending_documents()))]
        return []

    # -------------------------------------------------------------------------
    # AGGREGATES
    # -------------------------------------------------------------------------
    @api.model
    def _contract_facts(self, partners):
        """Contract count and market per customer, via the contract's lessee.

        `fleet.vehicle.log.contract.cliente_id` is the lessee who signed, which
        is the relation the customer's contract list hangs off. It used to be a
        stored compute mirroring the vehicle's driver and stayed empty on every
        record, so this joined on the driver instead; the field now carries the
        lessee and is what both the 360 and the contact form count on.

        The market comes from the contract too: `res.partner`'s own
        `fleet_customer_plaza_id` is empty for almost every customer, while the
        contract's `plaza_id` is populated.
        """
        contracts = self.env['fleet.vehicle.log.contract'].search([
            ('cliente_id', 'in', partners.ids),
        ], order='id desc')
        facts = {}
        for contract in contracts:
            fact = facts.setdefault(contract.cliente_id.id, {'count': 0, 'market': None})
            fact['count'] += 1
            if not fact['market']:
                fact['market'] = contract.plaza_id.name
        return facts

    @api.model
    def _partners_in_market(self, market):
        contracts = self.env['fleet.vehicle.log.contract'].search([
            ('plaza_id.name', 'ilike', market),
        ])
        return set(contracts.mapped('cliente_id').ids)

    @api.model
    def _policy_states(self, partners):
        """Worst policy state per customer, from `fleet.poliza.estado_vigencia`."""
        policies = self.env['fleet.poliza'].search([('cliente_id', 'in', partners.ids)])
        worst = {}
        for policy in policies:
            partner = policy.cliente_id.id
            state = policy.estado_vigencia
            if POLICY_SEVERITY.get(state, 0) >= POLICY_SEVERITY.get(worst.get(partner), -1):
                worst[partner] = state
        return worst

    @api.model
    def _vehicle_policy_state(self, vehicle):
        """Worst policy state among the vehicle's policies.

        A vehicle accumulates policies over the years, so the band reports the
        worst one rather than picking a "current" one, which the model has no
        field to identify.
        """
        if not vehicle:
            return None
        states = self.env['fleet.poliza'].search(
            [('vehiculo_id', '=', vehicle.id)]).mapped('estado_vigencia')
        if not states:
            return None
        return max(states, key=lambda s: POLICY_SEVERITY.get(s, 0))

    @api.model
    def _claim_counts(self, partners):
        claims = self.env['fleet.siniestro'].search([('cliente_id', 'in', partners.ids)])
        counts = dict.fromkeys(partners.ids, 0)
        for claim in claims:
            counts[claim.cliente_id.id] = counts.get(claim.cliente_id.id, 0) + 1
        return counts

    @api.model
    def _collection_facts(self, partners):
        """Worst collection standing per customer, from `credito.arrendamiento`.

        A customer can hold one credit per vehicle, so the board reports the
        worst: most days in arrears wins, and a payment plan is remembered even
        when it hangs off a different credit.
        """
        credits = self.env['credito.arrendamiento'].search([
            ('partner_id', 'in', partners.ids),
            ('estado', 'in', LIVE_CREDIT_STATES),
        ])
        facts = {}
        for credit in credits:
            fact = facts.setdefault(credit.partner_id.id,
                                    {'days': 0, 'plans': 0, 'due': 0.0, 'next_charge': None})
            fact['days'] = max(fact['days'], credit.dias_mora)
            fact['plans'] += credit.plan_pago_count
            fact['due'] += credit.saldo_exigible
            if credit.proximo_cargo_fecha and (
                    not fact['next_charge'] or credit.proximo_cargo_fecha < fact['next_charge']):
                fact['next_charge'] = credit.proximo_cargo_fecha
        return facts

    @api.model
    def _vehicle_collection_fact(self, vehicle):
        """Collection standing of the credit on one vehicle, for a contract card."""
        if not vehicle:
            return None
        credit = self.env['credito.arrendamiento'].search([
            ('vehiculo_id', '=', vehicle.id),
            ('estado', 'in', LIVE_CREDIT_STATES),
        ], limit=1)
        if not credit:
            return None
        return {'days': credit.dias_mora, 'plans': credit.plan_pago_count,
                'due': credit.saldo_exigible, 'next_charge': credit.proximo_cargo_fecha}

    @api.model
    def _document_facts(self, partners):
        """Vehicle paperwork per customer, from `fleet.tramite`.

        `estado_vigencia` is 'falta_subir' exactly when the trámite has no file
        attached, so the pending count is what the sheet calls "documents to
        handle". Nothing here is ever 'vencido' in this database because
        `fecha_vencimiento_renovacion` is empty, so expiry is not a signal yet.
        """
        paperwork = self.env['fleet.tramite'].search([('cliente_id', 'in', partners.ids)])
        facts = {}
        for tramite in paperwork:
            fact = facts.setdefault(tramite.cliente_id.id, {'total': 0, 'pending': 0})
            fact['total'] += 1
            if tramite.estado_vigencia == 'falta_subir':
                fact['pending'] += 1
        return facts

    @api.model
    def _vehicle_document_fact(self, vehicle):
        """Paperwork of one vehicle, for a contract card."""
        if not vehicle:
            return None
        paperwork = self.env['fleet.tramite'].search([('vehiculo_id', '=', vehicle.id)])
        if not paperwork:
            return None
        return {
            'total': len(paperwork),
            'pending': len(paperwork.filtered(lambda t: t.estado_vigencia == 'falta_subir')),
        }

    @api.model
    def _partners_with_pending_documents(self):
        paperwork = self.env['fleet.tramite'].search([('estado_vigencia', '=', 'falta_subir')])
        return set(paperwork.mapped('cliente_id').ids)

    @api.model
    def _ticket_facts(self, partners):
        """Open ticket count and worst SLA state per customer."""
        tickets = self.env['helpdesk.ticket'].search(
            OPEN_TICKET_DOMAIN + [('partner_id', 'in', partners.ids)])
        risk_limit = fields.Datetime.add(fields.Datetime.now(), hours=SLA_RISK_HOURS)
        facts = {}
        for ticket in tickets:
            fact = facts.setdefault(ticket.partner_id.id, {'count': 0, 'sla': 'on_time'})
            fact['count'] += 1
            if ticket.sla_fail or ticket.sla_reached_late:
                fact['sla'] = 'breached'
            elif fact['sla'] != 'breached' and ticket.sla_deadline and ticket.sla_deadline <= risk_limit:
                fact['sla'] = 'at_risk'
        return facts

    # -------------------------------------------------------------------------
    # DISPLAY HELPERS
    # -------------------------------------------------------------------------
    @api.model
    def _pending_display(self, hint):
        """Placeholder for a block whose source model is not wired yet."""
        return {'label': "—", 'tone': 'grey', 'pending': hint}

    @api.model
    def _policy_display(self, state):
        if not state:
            return self._pending_display(_("No policy on file"))
        labels = {
            'vigente': (_("Active"), 'green'),
            'falta_subir': (_("Missing upload"), 'amber'),
            'vencido': (_("Expired"), 'red'),
        }
        label, tone = labels[state]
        return {'label': label, 'tone': tone}

    @api.model
    def _collection_display(self, fact):
        """Arrears win over a payment plan: the board ranks by risk, not by effort."""
        if fact is None:
            return self._pending_display(_("No lease credit on file"))
        if fact['days'] > 0:
            return {'label': _("%s d overdue", fact['days']), 'tone': 'red',
                    'hint': _("On a payment plan") if fact['plans'] else None}
        if fact['plans']:
            return {'label': _("On payment plan"), 'tone': 'amber', 'hint': None}
        return {'label': _("Up to date"), 'tone': 'green', 'hint': None}

    @api.model
    def _collection_hint(self, fact):
        if fact is None:
            return _("No lease credit on file")
        if fact['plans']:
            return _("On a payment plan")
        if fact['next_charge']:
            return _("Next charge %s", format_date(self.env, fact['next_charge']))
        return _("From the customer's lease credit")

    @api.model
    def _document_display(self, fact):
        if fact is None:
            return self._pending_display(_("No paperwork on file"))
        if not fact['pending']:
            return {'label': _("Complete"), 'tone': 'green'}
        if fact['pending'] == 1:
            return {'label': _("1 pending"), 'tone': 'amber'}
        return {'label': _("%s pending", fact['pending']), 'tone': 'amber'}

    @api.model
    def _document_hint(self, fact):
        if fact is None:
            return _("No paperwork on file")
        return _("%(pending)s of %(total)s without their file",
                 pending=fact['pending'], total=fact['total'])

    @api.model
    def _ticket_display(self, count):
        if not count:
            return {'label': _("No open tickets"), 'tone': 'green'}
        label = _("1 open") if count == 1 else _("%s open", count)
        return {'label': label, 'tone': 'amber'}

    @api.model
    def _sla_display(self, count, sla_state):
        if not count:
            return {'label': "—", 'tone': 'grey'}
        labels = {
            'on_time': (_("On time"), 'green'),
            'at_risk': (_("At risk"), 'amber'),
            'breached': (_("SLA breached"), 'red'),
        }
        label, tone = labels[sla_state]
        return {'label': label, 'tone': tone}

    @api.model
    def _claim_display(self, count):
        if not count:
            return {'label': _("No claims"), 'tone': 'green'}
        label = _("1 in progress") if count == 1 else _("%s in progress", count)
        return {'label': label, 'tone': 'amber'}

    @api.model
    def _risk_level(self, policy_state, claim_count, sla_state, collection=None):
        overdue = bool(collection and collection['days'] > 0)
        on_plan = bool(collection and collection['plans'])
        if overdue or policy_state == 'vencido' or sla_state == 'breached':
            return 'red'
        if on_plan or policy_state == 'falta_subir' or sla_state == 'at_risk' or claim_count:
            return 'amber'
        return 'green'

    # -------------------------------------------------------------------------
    # BUSINESS METHODS
    # -------------------------------------------------------------------------
    @api.model
    def get_dashboard_data(self, search=None, quick_filter='all', offset=0, limit=ROWS_PER_PAGE):
        """One page of portfolio rows, plus KPIs over the whole filtered set."""
        domain = self._customer_domain(search) + self._quick_filter_domain(quick_filter)
        Partner = self.env['res.partner']

        total = Partner.search_count(domain)
        partners = Partner.search(domain, offset=offset, limit=limit, order='name, id')

        contracts = self._contract_facts(partners)
        policies = self._policy_states(partners)
        claims = self._claim_counts(partners)
        tickets = self._ticket_facts(partners)
        collections = self._collection_facts(partners)
        documents = self._document_facts(partners)

        clients = []
        for partner in partners:
            policy_state = policies.get(partner.id)
            claim_count = claims.get(partner.id, 0)
            ticket = tickets.get(partner.id, {'count': 0, 'sla': 'on_time'})
            contract = contracts.get(partner.id, {'count': 0, 'market': None})
            collection = collections.get(partner.id)
            document = documents.get(partner.id)
            clients.append({
                'id': partner.id,
                'partner_id': partner.id,
                'name': partner.name,
                'tax_id': partner.vat or "—",
                'signup_label': self._customer_since(partner),
                'market': contract['market'] or partner.fleet_customer_plaza_id.name or "—",
                'contract_count': contract['count'],
                'collection': self._collection_display(collection),
                'documents': self._document_display(document),
                'policy': self._policy_display(policy_state),
                'ticket_count': ticket['count'],
                'sla': self._sla_display(ticket['count'], ticket['sla']),
                'claim_count': claim_count,
                'risk_level': self._risk_level(policy_state, claim_count, ticket['sla'], collection),
            })

        return {
            'clients': clients,
            'kpis': self._portfolio_kpis(domain),
            'total': total,
            'offset': offset,
            'limit': limit,
        }

    @api.model
    def _portfolio_kpis(self, domain):
        Partner = self.env['res.partner']
        return {
            'active_portfolio': Partner.search_count(domain),
            'pending_documents': Partner.search_count(
                domain + [('id', 'in', list(self._partners_with_pending_documents()))]),
            'in_arrears': Partner.search_count(
                domain + [('id', 'in', list(self._partners_in_arrears()))]),
            'expired_policy': Partner.search_count(
                domain + [('id', 'in', list(self._partners_with_expired_policy()))]),
            'open_tickets': Partner.search_count(
                domain + [('id', 'in', list(self._partners_with_open_tickets()))]),
            'open_claims': Partner.search_count(
                domain + [('id', 'in', list(self._partners_with_claims()))]),
        }

    @api.model
    def get_client_detail(self, partner_id):
        """Full 360 sheet, aggregated from the modules that own each block."""
        partner = self.env['res.partner'].browse(partner_id)
        return {
            'client': {
                'id': partner.id,
                'partner_id': partner.id,
                'name': partner.name,
                'market': self._contract_facts(partner).get(partner.id, {}).get('market')
                          or partner.fleet_customer_plaza_id.name or "—",
                'signup_label': self._customer_since(partner),
            },
            **self._detail_sheet(partner),
            'indicator_labels': self._indicator_labels(),
            'has_contracts': bool(self._customer_contracts(partner)),
            'credit_form_view_id': self._form_view_id(
                'credito_arrendamiento.credito_arrendamiento_view_form'),
            'ticket_form_view_id': self._form_view_id('helpdesk.helpdesk_ticket_view_form'),
            'contract_form_view_id': self._form_view_id('fleet_contrato.fleet_contrato_view_form'),
            'claim_form_view_id': self._form_view_id('fleet_siniestro.fleet_siniestro_view_form'),
            'whatsapp_ready': self._whatsapp_available(),
        }

    @api.model
    def _whatsapp_available(self):
        """Whether the WhatsApp button has anywhere to go.

        Odoo's own predicate: it stays true for WhatsApp administrators even
        with no approved template, so they still get the wizard's "Configure
        Templates" redirect instead of a disabled button that explains nothing.
        Everyone else gets the button disabled rather than a dead end.
        """
        return self.env['whatsapp.template']._can_use_whatsapp('res.partner')

    @api.model
    def _form_view_id(self, xmlid):
        """Resolve a form view the sheet links to, pinned by external id.

        Returns None instead of raising so the client can let Odoo pick the
        model's default form if the view is ever renamed upstream. Worth the
        indirection here: `credito_arrendamiento` is mirrored from Nebula and
        `helpdesk` is Enterprise, so neither id is ours to guarantee.
        """
        view = self.env.ref(xmlid, raise_if_not_found=False)
        return view.id if view else None

    @api.model
    def _indicator_labels(self):
        """Captions of the 360 semaphore band, keyed as the payloads key them."""
        return {
            'collection': _("Collection"),
            'documents': _("Documents"),
            'policy': _("Insurance policy"),
            'tickets': _("Tickets"),
            'claims': _("Claims"),
        }

    # -------------------------------------------------------------------------
    # CONTRACT CARDS
    # -------------------------------------------------------------------------
    @api.model
    def _customer_since(self, partner):
        """Earliest contract start, falling back to when the record was created.

        `res.partner.create_date` is when the customer was imported into this
        database — February 2026 for the whole base — so it says nothing about
        how long they have been a customer.
        """
        first = self.env['fleet.vehicle.log.contract'].with_context(active_test=False).search(
            [('cliente_id', '=', partner.id), ('start_date', '!=', False)],
            order='start_date asc', limit=1)
        return format_date(self.env, first.start_date or partner.create_date, date_format="MMM y")

    @api.model
    def _customer_contracts(self, partner):
        """The customer's contracts, current ones first, then newest first.

        Archived contracts are included: the selector is a history, and a
        cancelled contract is part of what an agent needs to see.
        """
        contracts = self.env['fleet.vehicle.log.contract'].with_context(
            active_test=False).search([('cliente_id', '=', partner.id)])
        return contracts.sorted(
            key=lambda c: (c.state != 'open', -(c.start_date.toordinal() if c.start_date else 0)))

    @api.model
    def _rent_label(self, contract):
        if not contract.cost_generated:
            return "—"
        amount = formatLang(self.env, contract.cost_generated,
                            currency_obj=contract.company_id.currency_id)
        # cost_frequency carries trailing blanks in this database.
        frequency = (contract.cost_frequency or '').strip()
        if not frequency or frequency == 'no':
            return amount
        labels = dict(contract._fields['cost_frequency']._description_selection(self.env))
        return f"{amount} / {labels.get(frequency, frequency)}"

    @api.model
    def _contract_kind(self, contract):
        product = contract.producto_id.name
        if not contract.num_plazos:
            return product or "—"
        terms = _("%s terms", contract.num_plazos)
        return f"{product} · {terms}" if product else terms

    @api.model
    def _contract_alert(self, contract):
        """Right-hand note on the card: what an agent should notice about it."""
        if contract.state == 'open' and contract.expiration_date:
            return {'label': _("Ends %s", format_date(self.env, contract.expiration_date)),
                    'tone': 'green'}
        labels = dict(contract._fields['state']._description_selection(self.env))
        return {'label': labels.get(contract.state, "—"),
                'tone': CONTRACT_STATE_TONES.get(contract.state, 'grey')}

    # -------------------------------------------------------------------------
    # 360 DETAIL CARDS
    # -------------------------------------------------------------------------
    @api.model
    def _no_source(self, what):
        """Value for a fact no model holds yet. Kept explicit so the screen says
        "we don't know" instead of showing a plausible blank."""
        return {'value': "—", 'hint': _("No source yet: %s", what)}

    @api.model
    def _deposit_display(self, credit):
        """Security deposit slot, served from the credit's advance payments.

        `credito.arrendamiento` holds no deposit of its own, so the business
        reads `pagos_anticipados_acumulados` in that place for now. The hint
        names the real field so the figure is never mistaken for a settled
        guarantee.
        """
        if not credit:
            return self._no_source(_("security deposit"))
        return {
            'value': formatLang(self.env, credit.pagos_anticipados_acumulados,
                                currency_obj=credit.currency_id),
            'hint': _("Accumulated advance payments"),
        }

    @api.model
    def _studio_value(self, record, field_name):
        """Read a Studio field that not every database carries.

        The CIE, the payment CLABE and the collection agent were captured with
        Studio before the models had them. Those columns exist in production
        and in no other database, and reading a field a model does not define
        raises, so every read of one is optional by construction.
        """
        if not record or field_name not in record._fields:
            return None
        return record[field_name]

    @api.model
    def _leasing_details(self, contract, credit):
        vehicle = contract.vehicle_id
        deposit = self._deposit_display(credit)
        unit = ' · '.join(str(p) for p in (vehicle.color, vehicle.model_year) if p) or "—"
        if credit:
            frequency = dict(credit._fields['frecuencia']._description_selection(self.env)).get(
                credit.frecuencia)
        else:
            frequency = dict(contract._fields['cost_frequency']._description_selection(self.env)).get(
                (contract.cost_frequency or '').strip())
        paid, total = self._term_progress(contract, credit)
        return {
            'unit_color': unit,
            'registered': _("Registered %s", format_date(self.env, vehicle.acquisition_date))
                          if vehicle.acquisition_date else "—",
            'charge_day': _("Charged %s", frequency.lower()) if frequency else "—",
            'next_charge': format_date(self.env, credit.proximo_cargo_fecha)
                           if credit and credit.proximo_cargo_fecha else "—",
            'next_charge_hint': formatLang(self.env, credit.proximo_cargo_monto,
                                           currency_obj=contract.company_id.currency_id)
                                if credit and credit.proximo_cargo_monto else "—",
            'deposit': deposit['value'],
            'deposit_hint': deposit['hint'],
            'start_date': format_date(self.env, contract.start_date) if contract.start_date else "—",
            'end_date': format_date(self.env, contract.expiration_date) if contract.expiration_date else "—",
            'cie': contract.cie or self._studio_value(credit, 'x_studio_cie') or "—",
            'cie_hint': _("Payment reference of the contract"),
            'clabe': contract.clabe_pago
                     or self._studio_value(credit, 'x_studio_clabe_pago') or "—",
            'clabe_hint': _("Payment CLABE of the contract"),
            'progress_label': _("%(paid)s of %(total)s terms paid", paid=paid, total=total)
                              if credit and total else _("%s terms · schedule not loaded", total)
                              if total else _("Term progress unknown"),
            'progress_pct': round(100 * paid / total) if credit and total else 0,
            'source': "fleet.vehicle.log.contract + credito.arrendamiento",
        }

    @api.model
    def _term_progress(self, contract, credit):
        """Terms paid over the contract's total, from the credit's schedule."""
        total = contract.num_plazos or 0
        if not credit:
            return 0, total
        lines = credit.linea_ids
        paid = len(lines.filtered(lambda line: line.estado == 'pagada'))
        return paid, total or len(lines)

    @api.model
    def _collection_card(self, credit, fact):
        display = self._collection_display(fact)
        # The agent is named on the payment plan, not on the credit, so a
        # customer without a plan has nobody assigned to show.
        employee = self._studio_value(credit.plan_pago_ids[:1] if credit else None,
                                      'x_studio_gestor_encargado')
        agent = ({'value': employee.name, 'hint': None} if employee
                 else self._no_source(_("collection agent")))
        if not credit:
            return {
                'status': display['label'], 'tone': display['tone'],
                'summary': _("No lease credit on file"),
                'plan_label': _("Payment plan"), 'plan_title': "—", 'plan_hint': "—",
                'agent_label': _("Collection agent"), 'agent': agent['value'],
                'document': "—", 'links': [],
                'source': "credito.arrendamiento (sin registro para este contrato)",
            }
        currency = credit.currency_id
        plan = credit.plan_pago_ids[:1]
        if plan:
            statuses = dict(plan._fields['estatus']._description_selection(self.env))
            plan_title = _("%(periods)s installments of %(amount)s",
                           periods=plan.numero_periodos,
                           amount=formatLang(self.env, plan.pago_periodico_monto, currency_obj=currency))
            plan_hint = _("%(status)s · from %(start)s to %(end)s",
                          status=statuses.get(plan.estatus, "—"),
                          start=format_date(self.env, plan.fecha_inicio) if plan.fecha_inicio else "—",
                          end=format_date(self.env, plan.fecha_fin) if plan.fecha_fin else "—")
        else:
            plan_title, plan_hint = _("No payment plan"), "—"
        return {
            'status': display['label'], 'tone': display['tone'],
            'summary': _("%(due)s due · %(principal)s principal outstanding",
                         due=formatLang(self.env, credit.saldo_exigible, currency_obj=currency),
                         principal=formatLang(self.env, credit.saldo_principal_no_exigible,
                                              currency_obj=currency)),
            'plan_label': _("Payment plan"),
            'plan_title': plan_title,
            'plan_hint': plan_hint,
            'agent_label': _("Collection agent"),
            'agent': agent['value'],
            'document': "—",
            'links': [],
            'source': "credito.arrendamiento + credito.arrendamiento.plan.pago",
        }

    @api.model
    def _instalment_row(self, line, prefix, tag, tag_tone, amount, pending, currency):
        """One movement of the collection card, from either instalment model."""
        statuses = dict(line._fields['estado']._description_selection(self.env))
        tone = INSTALMENT_TONES.get(line.estado, 'grey')
        return {
            'id': f"{prefix}-{line.id}",
            'due': line.fecha_vencimiento,
            'label': _("Term %s", line.periodo),
            'tag': tag,
            'tag_tone': tag_tone,
            'amount': formatLang(self.env, amount, currency_obj=currency),
            'status': statuses.get(line.estado, "—"),
            'status_tone': tone,
            'risk': tone,
            'hint': _("Due %(date)s · %(pending)s outstanding",
                      date=format_date(self.env, line.fecha_vencimiento)
                           if line.fecha_vencimiento else "—",
                      pending=formatLang(self.env, pending, currency_obj=currency)),
        }

    @api.model
    def _collection_entries(self, credit):
        """Rent instalments and payment-plan instalments as one list.

        Both hang off the credit — `linea_ids` is the amortization schedule and
        `plan_pago_ids.linea_ids` is what was renegotiated — and neither points
        at a contract, so the credit is where they join.

        Only the `COLLECTION_ENTRIES_SHOWN` entries closest to today survive:
        the whole schedule can run to hundreds of terms, and an agent on a call
        needs what is about to fall due, not the first period of the lease.
        """
        if not credit:
            return []
        currency = credit.currency_id
        rows = [
            self._instalment_row(line, 'linea', _("Rent"), 'grey',
                                 line.pago_periodico, line.monto_pendiente, currency)
            for line in credit.linea_ids
        ] + [
            self._instalment_row(line, 'plan', _("Payment plan"), 'amber',
                                 line.monto_prometido, line.monto_pendiente_promesa, currency)
            for plan in credit.plan_pago_ids for line in plan.linea_ids
        ]

        today = fields.Date.context_today(self)
        # closest due date first; entries with no date go last
        rows.sort(key=lambda row: (row['due'] is None, abs((row['due'] - today).days)
                                   if row['due'] else 0))
        shown = rows[:COLLECTION_ENTRIES_SHOWN]
        # read them as a timeline once the window is chosen
        shown.sort(key=lambda row: (row['due'] is None, row['due'] or today))
        for row in shown:
            del row['due']
        return shown

    @api.model
    def _tickets_card(self, partner, contract_count):
        tickets = self.env['helpdesk.ticket'].search(
            OPEN_TICKET_DOMAIN + [('partner_id', '=', partner.id)], order='create_date desc')
        risk_limit = fields.Datetime.add(fields.Datetime.now(), hours=SLA_RISK_HOURS)
        items = []
        for ticket in tickets:
            if ticket.sla_fail or ticket.sla_reached_late:
                tone, clock = 'red', _("SLA breached")
            elif ticket.sla_deadline and ticket.sla_deadline <= risk_limit:
                tone, clock = 'amber', format_date(self.env, ticket.sla_deadline)
            else:
                tone, clock = 'green', format_date(self.env, ticket.sla_deadline) \
                    if ticket.sla_deadline else _("No SLA")
            items.append({
                'id': f"ticket-{ticket.id}",
                'title': ticket.name or "—",
                'meta': _("#%(ref)s · %(team)s · %(stage)s", ref=ticket.ticket_ref or ticket.id,
                          team=ticket.team_id.name or "—", stage=ticket.stage_id.name or "—"),
                'status': ticket.stage_id.name or "—",
                'tone': tone,
                'clock': clock,
                'progress': 100 if tone == 'red' else (70 if tone == 'amber' else 30),
            })
        return {
            'in_contract': len(tickets),
            'total': len(tickets),
            'items': items,
            'note': _("helpdesk.ticket has no link to a contract, so these are the "
                      "customer's open tickets across all of them."),
            'source': "helpdesk.ticket (+ SLA policy)",
        }

    @api.model
    def _claim_card(self, vehicle):
        claim = self.env['fleet.siniestro'].search(
            [('vehiculo_id', '=', vehicle.id)], order='id desc', limit=1) if vehicle else None
        if not claim:
            return {'empty': True, 'source': "fleet.siniestro (sin registro para este vehículo)"}
        photos = self.env['ir.attachment'].search_count([
            ('res_model', '=', 'fleet.siniestro'), ('res_id', '=', claim.id),
            ('res_field', '=', False)])
        return {
            'empty': False,
            'id': claim.id,
            'title': claim.siniestro_tipo_id.name or claim.folio or "—",
            'status': claim.etapa_id.name or "—",
            'meta': _("%(folio)s · %(date)s · %(plaza)s", folio=claim.folio or "—",
                      date=format_date(self.env, claim.fecha_hora_suceso) if claim.fecha_hora_suceso else "—",
                      plaza=claim.plaza_id.name or "—"),
            'description': claim.descripcion_siniestro or _("No description"),
            'insurer_line': _("Insurer %(insurer)s · deductible %(deductible)s · %(photos)s attachments",
                              insurer=claim.aseguradora_id.name or claim.aseguradora or "—",
                              deductible=formatLang(self.env, claim.deducible),
                              photos=photos),
            'repair_label': _("Repair status"),
            'repair_title': claim.taller or "—",
            'repair_hint': _("Estimated delivery %s",
                             format_date(self.env, claim.fecha_compromiso_entrega))
                           if claim.fecha_compromiso_entrega else "—",
            'contact_label': _("Ruling"),
            'contact_text': claim.dictamen or "—",
            'source': "fleet.siniestro",
        }

    @api.model
    def _delivery_advisor(self, vehicle):
        """Advisor who handed the unit over, which is what the business calls
        the salesperson. `agenda.entrega` has no link to the contract, so the
        vehicle is the join and the latest delivery wins: a unit that comes back
        and is leased again is delivered again, and the current lease is the one
        the sheet is about."""
        if not vehicle:
            return None
        delivery = self.env['agenda.entrega'].search(
            [('vehiculo_id', '=', vehicle.id), ('asesor_id', '!=', False)],
            order='id desc', limit=1)
        return delivery.asesor_id.name or None

    @api.model
    def _operations_rows(self, contract):
        vehicle = contract.vehicle_id
        app = self._no_source(_("operating app"))
        return [
            {'label': _("Market"), 'value': contract.plaza_id.name or "—"},
            {'label': _("Product"), 'value': contract.producto_id.name or "—"},
            {'label': _("Vehicle condition"), 'value': contract.condicion_vehiculo_id.name or "—"},
            {'label': _("Salesperson"), 'value': self._delivery_advisor(vehicle) or "—"},
            {'label': _("Operating app"), 'value': app['value']},
            {'label': _("Odometer"), 'value': _("%s km", int(vehicle.odometer)) if vehicle.odometer else "—"},
        ]

    @api.model
    def _documents_card(self, vehicle, document_fact):
        items = []
        if vehicle:
            tones = {'vigente': ('green', None), 'vencido': ('red', None),
                     'falta_subir': ('amber', None)}
            paperwork = self.env['fleet.tramite'].search(
                [('vehiculo_id', '=', vehicle.id)], order='id desc')
            statuses = dict(paperwork._fields['estado_vigencia']._description_selection(self.env)) \
                if paperwork else {}
            for tramite in paperwork:
                tone = tones.get(tramite.estado_vigencia, ('grey', None))[0]
                items.append({
                    'id': f"tramite-{tramite.id}",
                    'title': tramite.tipo_tramite_id.name or "—",
                    'hint': _("Filed %s", format_date(self.env, tramite.fecha_tramite))
                            if tramite.fecha_tramite else "—",
                    'status': statuses.get(tramite.estado_vigencia, "—"),
                    'tone': tone,
                })
            for policy in self.env['fleet.poliza'].search([('vehiculo_id', '=', vehicle.id)],
                                                          order='id desc', limit=3):
                display = self._policy_display(policy.estado_vigencia)
                items.append({
                    'id': f"poliza-{policy.id}",
                    # proveedor_polizas is a supplier *type* ("Pólizas de seguro"),
                    # not the insurer, so it earns no place in the title.
                    'title': _("Insurance policy"),
                    'hint': _("From %(start)s to %(end)s",
                              start=format_date(self.env, policy.fecha_inicio)
                                    if policy.fecha_inicio else "—",
                              end=format_date(self.env, policy.fecha_vencimiento)
                                  if policy.fecha_vencimiento else "—"),
                    'status': display['label'],
                    'tone': display['tone'],
                })
        return {
            'summary': self._document_hint(document_fact),
            'items': items,
            'vehicle_id': vehicle.id if vehicle else None,
            'source': "fleet.tramite + fleet.poliza",
        }

    @api.model
    def _interaction_card(self, partner):
        icons = {'WhatsApp': 'chat', 'Llamada': 'call'}
        interactions = self.env['atencion.cliente.interaccion'].search(
            [('cliente_id', '=', partner.id)], order='create_date desc', limit=5)
        if not interactions:
            # Always a dict: the sheet renders this card for every customer, and
            # a None here used to crash the whole 360 on the first customer with
            # no interaction logged.
            return {'channel': None, 'items': [],
                    'empty': _("No interaction logged for this customer")}
        items = []
        for interaction in interactions:
            channel = interaction.medio_contacto_id.name or "—"
            items.append({
                'id': f"interaccion-{interaction.id}",
                'icon': icons.get(channel, 'alert'),
                'text': interaction.comentario or interaction.tipo_solicitud_id.name or "—",
                'meta': _("%(folio)s · %(date)s · %(channel)s",
                          folio=interaction.folio or interaction.id,
                          date=format_date(self.env, interaction.create_date),
                          channel=channel),
            })
        return {'channel': interactions[0].medio_contacto_id.name or "—",
                'items': items, 'empty': None}

    @api.model
    def _contract_card(self, contract, partner_facts):
        """One entry of the contract selector, with its own semaphore band."""
        vehicle = contract.vehicle_id
        policy_state = self._vehicle_policy_state(vehicle)
        claim_count = self.env['fleet.siniestro'].search_count(
            [('vehiculo_id', '=', vehicle.id)]) if vehicle else 0

        collection_fact = self._vehicle_collection_fact(vehicle)
        document_fact = self._vehicle_document_fact(vehicle)
        credit = self.env['credito.arrendamiento'].search(
            [('vehiculo_id', '=', vehicle.id), ('estado', 'in', LIVE_CREDIT_STATES)], limit=1
        ) if vehicle else self.env['credito.arrendamiento']
        alert = self._contract_alert(contract)
        policy = self._policy_display(policy_state)
        claims = self._claim_display(claim_count)
        tickets = self._ticket_display(partner_facts['count'])
        collection = self._collection_display(collection_fact)
        documents = self._document_display(document_fact)
        state_labels = dict(contract._fields['state']._description_selection(self.env))

        return {
            'id': contract.id,
            'credit_id': credit.id or None,
            'reference': contract.ins_ref or contract.rec_name or str(contract.id),
            'status': state_labels.get(contract.state, "—"),
            'status_tone': CONTRACT_STATE_TONES.get(contract.state, 'grey'),
            'kind': self._contract_kind(contract),
            'unit': vehicle.model_id.display_name or vehicle.display_name or "—",
            'plates': vehicle.license_plate or "—",
            'vin': contract.vin_sn or "—",
            'weekly_rent': self._rent_label(contract),
            'alert': alert['label'],
            'alert_tone': alert['tone'],
            'details': self._leasing_details(contract, credit),
            'charge_types': [],
            'entries': self._collection_entries(credit),
            'collection': self._collection_card(credit, collection_fact),
            'tickets': self._tickets_card(contract.cliente_id, partner_facts['count']),
            'claim': self._claim_card(vehicle),
            'operations': self._operations_rows(contract),
            'operations_source': "fleet.vehicle.log.contract + fleet.vehicle + agenda.entrega",
            'documents': self._documents_card(vehicle, document_fact),
            'indicators': [
                {'key': 'collection', 'value': collection['label'],
                 'hint': self._collection_hint(collection_fact), 'tone': collection['tone']},
                {'key': 'documents', 'value': documents['label'],
                 'hint': self._document_hint(document_fact), 'tone': documents['tone']},
                {'key': 'policy', 'value': policy['label'],
                 'hint': _("Worst of the vehicle's policies"), 'tone': policy['tone']},
                {'key': 'tickets', 'value': tickets['label'],
                 'hint': _("Counted per customer, not per contract"), 'tone': tickets['tone']},
                {'key': 'claims', 'value': claims['label'],
                 'hint': _("Claims on this vehicle"), 'tone': claims['tone']},
            ],
        }

    @api.model
    def _detail_sheet(self, partner):
        """Profile, interaction log and one card per contract."""
        ticket_facts = self._ticket_facts(partner).get(partner.id, {'count': 0, 'sla': 'on_time'})
        contracts = [self._contract_card(c, ticket_facts)
                     for c in self._customer_contracts(partner)]

        if not contracts:
            policy = self._policy_display(self._policy_states(partner).get(partner.id))
            claims = self._claim_display(self._claim_counts(partner).get(partner.id, 0))
            tickets = self._ticket_display(ticket_facts['count'])
            collection_fact = self._collection_facts(partner).get(partner.id)
            collection = self._collection_display(collection_fact)
            document_fact = self._document_facts(partner).get(partner.id)
            documents = self._document_display(document_fact)
            contracts = [{
                'id': 0,
                'reference': _("No contract on file"),
                'status': "—",
                'status_tone': 'grey',
                'kind': "—",
                'unit': "—",
                'plates': "—",
                'vin': "—",
                'weekly_rent': "—",
                'alert': "—",
                'alert_tone': 'grey',
                'indicators': [
                    {'key': 'collection', 'value': collection['label'],
                     'hint': self._collection_hint(collection_fact), 'tone': collection['tone']},
                    {'key': 'documents', 'value': documents['label'],
                     'hint': self._document_hint(document_fact), 'tone': documents['tone']},
                    {'key': 'policy', 'value': policy['label'],
                     'hint': _("From the customer's policies"), 'tone': policy['tone']},
                    {'key': 'tickets', 'value': tickets['label'],
                     'hint': self._sla_display(ticket_facts['count'], ticket_facts['sla'])['label'],
                     'tone': tickets['tone']},
                    {'key': 'claims', 'value': claims['label'],
                     'hint': _("Claims on file"), 'tone': claims['tone']},
                ],
            }]

        return {
            'profile': {
                'phone': partner.phone or "—",
                'email': partner.email or "—",
                'gender': dict(partner._fields['genero'].selection).get(partner.genero, "—"),
                'account_manager': _("Unassigned"),
            },
            'interaction': self._interaction_card(partner),
            'contracts': contracts,
        }
