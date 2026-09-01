import { Component, onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const QUICK_FILTERS = [
    { key: "all", label: _t("All") },
    { key: "arrears", label: _t("In arrears") },
    { key: "documents", label: _t("Pending docs") },
    { key: "policy", label: _t("Expired policy") },
    { key: "ticket", label: _t("Open ticket") },
    { key: "claim", label: _t("With a claim") },
];

const AVATAR_COLOR_COUNT = 6;
const SEARCH_DEBOUNCE_MS = 300;

export class PortfolioDashboard extends Component {
    static template = "fleet_customer_portfolio.PortfolioDashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.quickFilters = QUICK_FILTERS;
        this.state = useState({
            loading: true,
            clients: [],
            kpis: {},
            search: "",
            activeFilter: "all",
            offset: 0,
            limit: 80,
            total: 0,
        });
        onWillStart(() => this.load());
    }

    async load() {
        this.state.loading = true;
        const data = await this.orm.call("fleet.customer.portfolio", "get_dashboard_data", [], {
            search: this.state.search.trim() || null,
            quick_filter: this.state.activeFilter,
            offset: this.state.offset,
            limit: this.state.limit,
        });
        this.state.clients = data.clients;
        this.state.kpis = data.kpis;
        this.state.total = data.total;
        this.state.loading = false;
    }

    /** Reload from the first page: any change of criteria invalidates the offset. */
    async reload() {
        this.state.offset = 0;
        await this.load();
    }

    onSearchInput(ev) {
        this.state.search = ev.target.value;
        clearTimeout(this.searchTimer);
        this.searchTimer = setTimeout(() => this.reload(), SEARCH_DEBOUNCE_MS);
    }

    setFilter(key) {
        this.state.activeFilter = key;
        this.reload();
    }

    get pageStart() {
        return this.state.total ? this.state.offset + 1 : 0;
    }

    get pageEnd() {
        return Math.min(this.state.offset + this.state.limit, this.state.total);
    }

    get countLabel() {
        return _t("Showing %s-%s of %s customers.", this.pageStart, this.pageEnd, this.state.total);
    }

    get hasPrevious() {
        return this.state.offset > 0;
    }

    get hasNext() {
        return this.pageEnd < this.state.total;
    }

    previousPage() {
        this.state.offset = Math.max(0, this.state.offset - this.state.limit);
        this.load();
    }

    nextPage() {
        this.state.offset += this.state.limit;
        this.load();
    }

    contractsLabel(client) {
        if (!client.contract_count) {
            return "—";
        }
        return client.contract_count === 1
            ? _t("1 contract")
            : _t("%s contracts", client.contract_count);
    }

    claimsLabel(client) {
        if (!client.claim_count) {
            return "—";
        }
        return client.claim_count === 1 ? _t("1 open") : _t("%s open", client.claim_count);
    }

    clientSubtitle(client) {
        return _t("%s · since %s", client.tax_id, client.signup_label);
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

    avatarClass(name) {
        let hash = 0;
        for (const char of name) {
            hash = (hash * 31 + char.charCodeAt(0)) % AVATAR_COLOR_COUNT;
        }
        return `o_fcp_avatar_${hash}`;
    }

    openClientDetail(client) {
        this.actionService.doAction({
            type: "ir.actions.client",
            tag: "fleet_customer_portfolio_detail",
            name: client.name,
            params: { client_id: client.id },
        });
    }
}

registry.category("actions").add("fleet_customer_portfolio", PortfolioDashboard);
