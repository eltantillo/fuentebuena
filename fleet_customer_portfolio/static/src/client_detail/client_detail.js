import { Component, markup, onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class ClientDetail extends Component {
    static template = "fleet_customer_portfolio.ClientDetail";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({
            loading: true,
            data: null,
            contractIndex: 0,
        });
        const clientId = this.props.action.params.client_id;
        onWillStart(async () => {
            this.state.data = await this.orm.call(
                "fleet.customer.portfolio",
                "get_client_detail",
                [clientId]
            );
            this.state.loading = false;
        });
    }

    get contract() {
        return this.state.data.contracts[this.state.contractIndex];
    }

    indicatorLabel(key) {
        return this.state.data.indicator_labels[key];
    }

    get contractsLead() {
        if (!this.state.data.has_contracts) {
            return _t("This customer has no contract on file.");
        }
        const count = this.state.data.contracts.length;
        if (count === 1) {
            return _t("One contract on file.");
        }
        return _t(
            "%s contracts on file, current ones first. Pick the one the enquiry is about — the band above changes with it.",
            count
        );
    }

    get pendingSheetNote() {
        return _t(
            "The detailed sheet — leasing terms, collection, tickets and claim — is not wired to real data yet. The band above already reads the vehicle's policies and claims."
        );
    }

    get contractHeading() {
        return _t("Pure leasing · Contract %s", this.contract.reference);
    }

    /** Same wizard the chatter opens, on the customer's record. */
    openWhatsapp() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: _t("Send WhatsApp Message"),
            res_model: "whatsapp.composer",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: {
                active_model: "res.partner",
                active_id: this.state.data.client.partner_id,
            },
        });
    }

    /** One record on its native form, in place of the sheet. */
    openRecord(resModel, resId, viewId, name) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: resModel,
            res_id: resId,
            view_mode: "form",
            views: [[viewId || false, "form"]],
            target: "current",
        });
    }

    /** A filtered list of records, so the agent lands on this customer's own. */
    openList(resModel, domain, name) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: resModel,
            domain,
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    openContract() {
        this.openRecord("fleet.vehicle.log.contract", this.contract.id,
                        this.state.data.contract_form_view_id, _t("Leasing contract"));
    }

    openClaim() {
        this.openRecord("fleet.siniestro", this.contract.claim.id,
                        this.state.data.claim_form_view_id, _t("Claim"));
    }

    openPaperwork() {
        this.openList("fleet.tramite",
                      [["vehiculo_id", "=", this.contract.documents.vehicle_id]],
                      _t("Vehicle paperwork"));
    }

    openInteractions() {
        this.openList("atencion.cliente.interaccion",
                      [["cliente_id", "=", this.state.data.client.partner_id]],
                      _t("Interaction history"));
    }

    /** New helpdesk ticket for this customer, on the native form. */
    createTicket() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: _t("New Ticket"),
            res_model: "helpdesk.ticket",
            view_mode: "form",
            views: [[this.state.data.ticket_form_view_id || false, "form"]],
            target: "current",
            // Only the customer is seeded; the rest is left to Odoo's own
            // defaults for the model.
            context: { default_partner_id: this.state.data.client.partner_id },
        });
    }

    /** Open the lease credit of the selected contract on its own form. */
    openAmortization() {
        const viewId = this.state.data.credit_form_view_id;
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "credito.arrendamiento",
            res_id: this.contract.credit_id,
            views: [[viewId || false, "form"]],
            target: "current",
        });
    }

    get ticketsInContractLabel() {
        return _t("%s on this contract", this.contract.tickets.in_contract);
    }

    get ticketsTotalLabel() {
        return _t("%s across all contracts", this.contract.tickets.total);
    }

    unitPlatesLabel(item) {
        return _t("Plates %s · VIN %s", item.plates, item.vin);
    }

    weeklyRentLabel(item) {
        return _t("Weekly rent %s", markup`<b>${item.weekly_rent}</b>`);
    }

    selectContract(index) {
        this.state.contractIndex = index;
    }

    initials(name) {
        return name
            .split(" ")
            .filter(Boolean)
            .slice(0, 2)
            .map((word) => word[0])
            .join("")
            .toUpperCase();
    }

    backToPortfolio() {
        this.actionService.doAction("fleet_customer_portfolio.action_customer_portfolio");
    }
}

registry.category("actions").add("fleet_customer_portfolio_detail", ClientDetail);
