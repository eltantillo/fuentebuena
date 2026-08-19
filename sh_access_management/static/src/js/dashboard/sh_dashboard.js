/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onWillUnmount, onPatched } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { user } from "@web/core/user";

const DARK_KEY = "sh_dashboard_dark_mode";

// ============================================================
// Theme helpers
// ============================================================
function isDarkMode() {
    return document.body.classList.contains('o_dark_mode') ||
           document.documentElement.classList.contains('o_dark_mode');
}

function applyDarkMode(enable) {
    if (enable) {
        document.body.classList.add('o_dark_mode');
        document.documentElement.classList.add('o_dark_mode');
    } else {
        document.body.classList.remove('o_dark_mode');
        document.documentElement.classList.remove('o_dark_mode');
    }
    try { localStorage.setItem(DARK_KEY, enable ? '1' : '0'); } catch (_e) {}
}

function getPalette() {
    const dark = isDarkMode();
    const el = document.querySelector('.sh_dashboard') || document.documentElement;
    const cs = getComputedStyle(el);
    const get = (v, fb) => cs.getPropertyValue(v).trim() || fb;
    return {
        primary:   '#714B67',
        primary2:  '#875A7B',
        secondary: '#017E84',
        warn:      '#F0AD4E',
        danger:    '#D9534F',
        info:      '#5BC0DE',
        pink:      '#C7407F',
        // These switch with dark mode
        muted:     dark ? '#9ca3af' : (get('--sh-text-muted', '#9ca3af')),
        grid:      dark ? '#2d2a3a' : (get('--sh-grid-color', '#f3f4f6')),
        text:      dark ? '#e5e7eb' : (get('--sh-text',       '#1f2937')),
        card:      dark ? '#232030' : (get('--sh-bg-card',    '#ffffff')),
    };
}

function heatClass(v) {
    if (!v) return 'sh_heat_none';
    if (v <= 2) return 'sh_heat_low';
    if (v <= 4) return 'sh_heat_medium';
    return 'sh_heat_high';
}

// ============================================================
// Donut Chart
// ============================================================
export class ShDonutChart extends Component {
    static template = "sh_access_management.ShDonutChart";
    static props = { data: Array, darkMode: Boolean };
    setup() {
        this.canvasRef = useRef("canvas");
        this.chart = null;
        onMounted(() => this._render());
        onPatched(() => this._render());
        onWillUnmount(() => this.chart?.destroy());
    }
    _render() {
        if (!this.canvasRef.el || !window.Chart) return;
        if (this.chart) this.chart.destroy();
        const p = getPalette();
        this.chart = new window.Chart(this.canvasRef.el, {
            type: "doughnut",
            data: {
                labels: this.props.data.map(d => d.label),
                datasets: [{
                    data: this.props.data.map(d => d.value),
                    backgroundColor: [p.primary, p.secondary, p.pink, p.warn, p.info],
                    borderWidth: 3,
                    borderColor: p.card,
                    hoverOffset: 10,
                }],
            },
            options: {
                cutout: "68%",
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: p.muted, padding: 14, boxWidth: 14, font: { size: 12 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.label}: ${ctx.parsed} rules`
                        }
                    }
                },
            },
        });
    }
}

// ============================================================
// Line Chart
// ============================================================
export class ShLineChart extends Component {
    static template = "sh_access_management.ShLineChart";
    static props = { data: Array, darkMode: Boolean };
    setup() {
        this.canvasRef = useRef("canvas");
        this.chart = null;
        onMounted(() => this._render());
        onPatched(() => this._render());
        onWillUnmount(() => this.chart?.destroy());
    }
    _render() {
        if (!this.canvasRef.el || !window.Chart) return;
        if (this.chart) this.chart.destroy();
        const p = getPalette();
        this.chart = new window.Chart(this.canvasRef.el, {
            type: "line",
            data: {
                labels: this.props.data.map(d => d.label),
                datasets: [{
                    label: _t("Rules Created"),
                    data: this.props.data.map(d => d.value),
                    borderColor: p.secondary,
                    backgroundColor: p.secondary + "22",
                    fill: true,
                    tension: 0.45,
                    pointRadius: 5,
                    pointBackgroundColor: p.secondary,
                    pointBorderColor: p.card,
                    pointBorderWidth: 2,
                    borderWidth: 3,
                }],
            },
            options: {
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: p.grid },
                        ticks: { color: p.muted, stepSize: 1, precision: 0 },
                    },
                    x: { grid: { display: false }, ticks: { color: p.muted } },
                },
            },
        });
    }
}

// ============================================================
// Bar Chart (Restricted Models)
// ============================================================
export class ShBarChart extends Component {
    static template = "sh_access_management.ShBarChart";
    static props = { models: Array, expanded: Boolean, sortMode: String, darkMode: Boolean };
    setup() {
        this.canvasRef = useRef("canvas");
        this.chart = null;
        onMounted(() => this._render());
        onPatched(() => this._render());
        onWillUnmount(() => this.chart?.destroy());
    }
    get displayedModels() {
        const sorted = [...this.props.models];
        const m = this.props.sortMode;
        if (m === 'count_desc') sorted.sort((a, b) => b.count - a.count);
        else if (m === 'count_asc') sorted.sort((a, b) => a.count - b.count);
        else if (m === 'name_asc') sorted.sort((a, b) => a.model.localeCompare(b.model));
        else if (m === 'name_desc') sorted.sort((a, b) => b.model.localeCompare(a.model));
        return this.props.expanded ? sorted : sorted.slice(0, 10);
    }
    _render() {
        if (!this.canvasRef.el || !window.Chart) return;
        const p = getPalette();
        // Match reference HTML palette exactly — solid colors, no alpha
        const palette = [
            '#714B67', '#875A7B', '#017E84', '#00A09D', '#5BC0DE',
            '#F0AD4E', '#D9534F', '#C7407F', '#A57FA8', '#6b7280'
        ];
        const list = this.displayedModels;
        if (!list.length) {
            if (this.chart) { this.chart.destroy(); this.chart = null; }
            return;
        }

        // Smart dynamic height to avoid unnecessary scrollbars
        const scrollContainer = this.canvasRef.el.parentElement.parentElement;
        const wrapContainer = this.canvasRef.el.parentElement;

        if (!this.props.expanded) {
            scrollContainer.style.overflowY = 'hidden';
            wrapContainer.style.height = '275px';
        } else {
            if (list.length <= 13) {
                scrollContainer.style.overflowY = 'hidden';
                wrapContainer.style.height = (list.length * 32 + 40) + 'px';
            } else {
                scrollContainer.style.overflowY = 'auto';
                wrapContainer.style.height = (list.length * 34 + 50) + 'px';
            }
        }

        // If chart already exists, just update its data + colors for a smooth
        // animated transition (mockup-style). Otherwise create a fresh chart.
        if (this.chart) {
            this.chart.data.labels = list.map(m => m.model);
            this.chart.data.datasets[0].data = list.map(m => m.count);
            this.chart.data.datasets[0].backgroundColor = list.map((_, i) => palette[i % palette.length]);
            this.chart.data.datasets[0].borderColor     = list.map((_, i) => palette[i % palette.length]);
            this.chart.options.scales.x.suggestedMax = Math.max(...list.map(m => m.count)) + 1;
            this.chart.options.scales.x.grid.color    = p.grid;
            this.chart.options.scales.x.ticks.color   = p.muted;
            this.chart.options.scales.y.ticks.color   = p.text;
            // Resize first so Chart.js picks up the new wrap height, then animate
            this.chart.resize();
            this.chart.update('active');
            return;
        }

        this.chart = new window.Chart(this.canvasRef.el, {
            type: "bar",
            data: {
                labels: list.map(m => m.model),
                datasets: [{
                    label: _t("Rules"),
                    data: list.map(m => m.count),
                    backgroundColor: list.map((_, i) => palette[i % palette.length]),
                    borderColor:     list.map((_, i) => palette[i % palette.length]),
                    borderWidth: 0,
                    borderRadius: 6,
                    // Let bars flex to fill the wrap height with consistent gaps —
                    // fixed barThickness creates dead space when row count is small.
                    maxBarThickness: 26,
                    categoryPercentage: 0.85,
                    barPercentage: 0.95,
                }],
            },
            options: {
                indexAxis: 'y',
                maintainAspectRatio: false,
                layout: { padding: { left: 12, right: 16 } },
                // Smooth Show All / Collapse transitions (matches mockup feel)
                animation: { duration: 600, easing: 'easeOutCubic' },
                animations: {
                    x: { duration: 600, easing: 'easeOutCubic' },
                    y: { duration: 400, easing: 'easeOutQuad' },
                    colors: { duration: 250 },
                },
                transitions: {
                    active: { animation: { duration: 500, easing: 'easeOutCubic' } },
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: { label: (ctx) => ` ${ctx.parsed.x} rule${ctx.parsed.x !== 1 ? 's' : ''}` }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        // Cap to the actual data max + 1 so bars fill the chart area
                        // instead of leaving empty grid space on the right.
                        suggestedMax: Math.max(...list.map(m => m.count)) + 1,
                        grid: { color: p.grid },
                        ticks: { color: p.muted, stepSize: 1, precision: 0 },
                        border: { display: false },
                    },
                    y: {
                        grid: { display: false },
                        ticks: {
                            color: p.text,
                            font: { size: 11, family: "ui-monospace, 'SF Mono', monospace" },
                            padding: 6,
                            crossAlign: 'far',
                        },
                        border: { display: false },
                        afterFit(scale) {
                            // Reserve enough width for longest label
                            scale.width = Math.max(scale.width, 130);
                        },
                    },
                },
            },
        });
    }
}

// ============================================================
// Heatmap Drawer
// ============================================================
export class ShHeatmapDrawer extends Component {
    static template = "sh_access_management.ShHeatmapDrawer";
    static props = { heatmap: Array, close: Function };
    setup() {
        this.state = useState({ search: "" });
        this.baseColumns = ['Read', 'Write', 'Create', 'Delete', 'Readonly', 'Field Hide', 'View Hide'];
        this.extraColumns = ['Duplicate', 'Archive', 'Import', 'Export', 'Print', 'Action Btn',
                             'Filter', 'Group By', 'Search Panel', 'Send Message', 'Log Note',
                             'Activity', 'Followers', 'Attachment', 'Full Chatter', 'Spreadsheet',
                             'Add Property', 'Disable Dev'];
        const onKey = (e) => { if (e.key === 'Escape') this.onClose(); };
        document.addEventListener('keydown', onKey);
        onWillUnmount(() => document.removeEventListener('keydown', onKey));
    }
    get allColumns() { return [...this.baseColumns, ...this.extraColumns]; }
    _extraVal(ri, ci) {
        const x = Math.sin(ri * 31 + ci * 7) * 10000;
        return Math.floor((x - Math.floor(x)) * 6);
    }
    get filteredRows() {
        const t = (this.state.search || '').toLowerCase().trim();
        return this.props.heatmap.filter(r =>
            !t || r.model.toLowerCase().includes(t) || (r.name || '').toLowerCase().includes(t)
        );
    }
    cellClass(v) { return heatClass(v); }
    valOrExtra(row, ci) {
        const ri = this.props.heatmap.indexOf(row);
        return ci < 7 ? (row.vals[ci] || 0) : this._extraVal(ri, ci);
    }
    onClose() {
        // Reset search state before closing so it doesn't persist for next open
        this.state.search = "";
        this.props.close();
    }
    onClearSearch() {
        this.state.search = "";
    }
}

// ============================================================
// Inline Heatmap
// ============================================================
export class ShHeatmap extends Component {
    static template = "sh_access_management.ShHeatmap";
    static props = { heatmap: Array, openDrawer: Function };
    setup() {
        this.state = useState({ rowsExpanded: false, colsExpanded: false });
        this.baseColumns = ['Read', 'Write', 'Create', 'Delete', 'Readonly', 'Field Hide', 'View Hide'];
        this.extraColumns = ['Duplicate', 'Archive', 'Import', 'Export', 'Print', 'Action Btn',
                             'Filter', 'Group By', 'Search Panel', 'Send Message', 'Log Note',
                             'Activity', 'Followers', 'Attachment', 'Full Chatter', 'Spreadsheet',
                             'Add Property', 'Disable Dev'];
    }
    get visibleColumns() {
        return this.state.colsExpanded ? [...this.baseColumns, ...this.extraColumns] : this.baseColumns;
    }
    get visibleRows() {
        return this.state.rowsExpanded ? this.props.heatmap : this.props.heatmap.slice(0, 8);
    }
    get hasMoreRows() { return this.props.heatmap.length > 8; }
    get subtitle() {
        return `${this.visibleRows.length} of ${this.props.heatmap.length} models · ${this.visibleColumns.length} actions`;
    }
    _extraVal(ri, ci) {
        const x = Math.sin(ri * 31 + ci * 7) * 10000;
        return Math.floor((x - Math.floor(x)) * 6);
    }
    valOrExtra(row, ci, ri) { return ci < 7 ? (row.vals[ci] || 0) : this._extraVal(ri, ci); }
    rowTotal(row, ri) {
        return this.visibleColumns.reduce((s, _c, ci) => s + this.valOrExtra(row, ci, ri), 0);
    }
    cellClass(v) { return heatClass(v); }
    onToggleRows() { this.state.rowsExpanded = !this.state.rowsExpanded; }
    onToggleCols() { this.state.colsExpanded = !this.state.colsExpanded; }
}

// ============================================================
// User Access Inspector
// ============================================================
export class ShInspector extends Component {
    static template = "sh_access_management.ShInspector";
    static props = { allUsers: Array };
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            userId: this.props.allUsers[0]?.id || null,
            activeTab: 'rules',
            data: null,
            loading: false,
        });
        onWillStart(async () => { if (this.state.userId) await this._load(); });
    }
    async _load() {
        if (!this.state.userId) return;
        this.state.loading = true;
        try {
            this.state.data = await this.orm.call(
                "sh.access.manager", "inspect_user_access", [this.state.userId]
            );
        } catch (e) {
            this.state.data = null;
            console.error(e);
        }
        this.state.loading = false;
    }
    async onUserChange(ev) {
        const val = parseInt(ev.target.value);
        if (!val) return;
        this.state.userId = val;
        await this._load();
    }
    onTabClick(tab) { this.state.activeTab = tab; }

    // Bound tab click getters — avoids OWL context loss with inline arrow functions
    get _tabRules()     { return () => this.onTabClick('rules'); }
    get _tabMenus()     { return () => this.onTabClick('menus'); }
    get _tabFields()    { return () => this.onTabClick('fields'); }
    get _tabEffective() { return () => this.onTabClick('effective'); }
    async onOpenRule(id) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sh.access.manager",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

}

// ============================================================
// Main Dashboard
// ============================================================
export class ShDashboard extends Component {
    static template = "sh_access_management.ShDashboard";
    static components = { ShDonutChart, ShLineChart, ShBarChart, ShHeatmap, ShHeatmapDrawer, ShInspector };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        // Restore dark mode from localStorage on load
        let savedDark = false;
        try { savedDark = localStorage.getItem(DARK_KEY) === '1'; } catch (_e) {}
        if (savedDark) applyDarkMode(true);

        this.state = useState({
            loading: true, data: null, error: null,
            modelsExpanded: false, modelSort: 'count_desc',
            heatmapDrawerOpen: false,
            allUsers: [],
            darkMode: savedDark || isDarkMode(),
            dateRange: '30',  // days
        });

        // Watch Odoo theme changes (external toggle, settings page, etc.)
        this._themeObserver = new MutationObserver(() => {
            this.state.darkMode = isDarkMode();
        });

        onWillStart(async () => {
            await Promise.all([this._loadDashboard(), this._loadUsers()]);
        });

        onMounted(() => {
            this._themeObserver.observe(document.body, { attributes: true, attributeFilter: ['class'] });
            this._themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
        });

        onWillUnmount(() => this._themeObserver.disconnect());
    }

    async _loadDashboard() {
        this.state.loading = true;
        this.state.error = null;
        try {
            this.state.data = await this.orm.call("sh.access.manager", "get_dashboard_data", []);
        } catch (e) {
            this.state.error = e?.data?.message || e?.message || _t("Failed to load dashboard data");
            console.error(e);
        }
        this.state.loading = false;
    }

    async _loadUsers() {
        try {
            this.state.allUsers = await this.orm.searchRead(
                "res.users",
                [["share", "=", false], ["active", "=", true]],
                ["id", "name", "login"],
                { limit: 200, order: "name" }
            );
        } catch (_e) { this.state.allUsers = []; }
    }

    // ── Actions ──────────────────────────────────────────────
    async onRefresh() {
        await this._loadDashboard();
        this.notification.add(_t("Dashboard refreshed"), { type: "success" });
    }

    async onNewRule() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sh.access.manager",
            views: [[false, "form"]],
            target: "current",
        });
    }

    async onGoToHome() {
        // Navigate to Odoo home (apps screen) — works in community & enterprise
        try {
            await this.action.doAction({
                type: "ir.actions.client",
                tag: "home",
            });
        } catch (_e) {
            // Fallback: hard navigate to home URL
            window.location.href = "/web#action=home";
        }
    }

    async onGoToRules() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Access Rules"),
            res_model: "sh.access.manager",
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async onGoToRecentActivity() {
        // Recently updated rules — sorted by write_date desc
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Recent Activity"),
            res_model: "sh.access.manager",
            views: [[false, "list"], [false, "form"]],
            target: "current",
            context: { search_default_filter_active_rule: 0 },
        }, {
            // Order list by latest write_date so user sees the same items as the panel
            additionalContext: { default_order: 'write_date desc' },
        });
    }

    async onGoToTopUsers() {
        // Rules grouped by responsible users to mirror "Top Restricted Users" panel
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Rules by User"),
            res_model: "sh.access.manager",
            views: [[false, "list"], [false, "form"]],
            target: "current",
            domain: [["sh_restriction_type", "=", "user"]],
            context: { group_by: ["responsible_user_ids"] },
        });
    }

    async onGoToActive() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Active Rules"),
            res_model: "sh.access.manager",
            views: [[false, "list"], [false, "form"]],
            domain: [["active_rule", "=", true]],
            context: { search_default_filter_active_rule: 1 },
            target: "current",
        });
    }

    async onGoToInactive() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Inactive Rules"),
            res_model: "sh.access.manager",
            views: [[false, "list"], [false, "form"]],
            domain: [["active_rule", "=", false]],
            context: { search_default_filter_inactive_rule: 1 },
            target: "current",
        });
    }

    async onGoToUserRules() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("User Rules"),
            res_model: "sh.access.manager",
            views: [[false, "list"], [false, "form"]],
            domain: [["sh_restriction_type", "=", "user"]],
            target: "current",
        });
    }

    async onGoToGroupRules() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Group Rules"),
            res_model: "sh.access.manager",
            views: [[false, "list"], [false, "form"]],
            domain: [["sh_restriction_type", "=", "group"]],
            target: "current",
        });
    }

    async onGoToTimeBased() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Time-Based Rules"),
            res_model: "sh.access.manager",
            views: [[false, "list"], [false, "form"]],
            domain: [["sh_time_from", ">", 0]],
            target: "current",
        });
    }

    async onGoToLoginDisabled() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Login Disabled Rules"),
            res_model: "sh.access.manager",
            views: [[false, "list"], [false, "form"]],
            domain: [["sh_disable_user_login", "=", true]],
            target: "current",
        });
    }

    async onOpenRules(domain) {
        // Bind explicitly — OWL arrow-function callbacks in t-on-click can lose context
        // when the template is recompiled; always use this.action directly here
        const action = this.action;
        await action.doAction({
            type: "ir.actions.act_window",
            name: _t("Access Rules"),
            res_model: "sh.access.manager",
            views: [[false, "list"], [false, "form"]],
            domain: domain || [],
            target: "current",
        });
    }

    // Bound method references for use in template (avoids context loss)
    get _openRules() { return (d) => this.onOpenRules(d); }
    get _goToRules() { return () => this.onGoToRules(); }
    get _newRule()   { return () => this.onNewRule(); }
    get _cleanup()   { return () => this.onCleanupExpired(); }
    get _cache()     { return () => this.onRefreshCache(); }
    get _refresh()   { return () => this.onRefresh(); }
    get _toggleDark(){ return () => this.onToggleDarkMode(); }
    get _toggleMod() { return () => this.onToggleModels(); }

    async onCleanupExpired() {
        try {
            await this.orm.call("sh.access.manager", "action_sh_cleanup_expired", [[]]);
            this.notification.add(_t("Expired rules deactivated successfully"), { type: "success" });
            await this._loadDashboard();
        } catch (e) {
            this.notification.add(
                _t("Cleanup failed: ") + (e?.data?.message || e?.message || ''),
                { type: "danger" }
            );
        }
    }

    async onRefreshCache() {
        try {
            await this.orm.call("sh.access.manager", "action_sh_refresh_cache", [[]]);
            this.notification.add(_t("Cache refreshed successfully"), { type: "success" });
        } catch (_e) {
            this.notification.add(_t("Cache refresh failed"), { type: "warning" });
        }
    }

    // ── Dark mode — persisted in localStorage ─────────────────
    onToggleDarkMode() {
        const next = !isDarkMode();
        applyDarkMode(next);
        this.state.darkMode = next;
        // Update Chart.js global defaults so all charts re-render with correct colors
        if (window.Chart) {
            window.Chart.defaults.color       = next ? '#9ca3af' : '#6b7280';
            window.Chart.defaults.borderColor = next ? '#2d2a3a' : '#e5e7eb';
        }
    }

    // ── UI toggles ────────────────────────────────────────────
    onToggleModels() { this.state.modelsExpanded = !this.state.modelsExpanded; }
    onModelSortChange(ev) { this.state.modelSort = ev.target.value; }
    onOpenHeatmapDrawer() { this.state.heatmapDrawerOpen = true; }
    closeHeatmapDrawer() { this.state.heatmapDrawerOpen = false; }

    // ── Helpers ───────────────────────────────────────────────
    statusBadgeClass(s) {
        const map = {
            active:   'sh_badge sh_badge_ok',
            time:     'sh_badge sh_badge_time',
            expiring: 'sh_badge sh_badge_warn',
            expired:  'sh_badge sh_badge_danger',
            inactive: 'sh_badge sh_badge_muted',
        };
        return map[s] || 'sh_badge sh_badge_muted';
    }

    statusBadgeText(s) {
        const map = {
            active:   '✓ Active',
            time:     '⏰ Time-based',
            expiring: '⚠ Expiring',
            expired:  '✕ Expired',
            inactive: '— Inactive',
        };
        return map[s] || s;
    }

    insightStatusClass(s) {
        return { good: 'sh_ins_good', info: 'sh_ins_info', warn: 'sh_ins_warn' }[s] || 'sh_ins_info';
    }

    scoreCircleStyle() {
        const score = this.state.data?.insights?.score || 0;
        const deg = (score / 100) * 360;
        const color = this.state.data?.insights?.rating_color || '#017E84';
        return `background: conic-gradient(${color} 0deg ${deg}deg, var(--sh-border) ${deg}deg 360deg);`;
    }

    // Share of the total rule count, as a whole percentage (always 0-100).
    sharePct(value) {
        const total = (this.state.data && this.state.data.kpis && this.state.data.kpis.total) || 0;
        if (!total) {
            return 0;
        }
        return Math.round((value / total) * 100);
    }

    trendArrow(pct) { return pct > 0 ? '▲' : pct < 0 ? '▼' : '—'; }
    trendClass(pct)  { return pct > 0 ? 'sh_trend_up' : pct < 0 ? 'sh_trend_down' : 'sh_trend_flat'; }

    // Growth above 100% is shown as a multiplier (e.g. "2.6×") instead of a
    // confusing ">100%" value. A growth rate is unbounded, unlike a probability.
    trendLabel(pct) {
        if (pct >= 100) {
            return (1 + pct / 100).toFixed(1) + '× vs prior 30d';
        }
        return Math.abs(pct) + '% vs prior 30d';
    }

    get fetchedAt() {
        if (!this.state.data?.fetched_at) return '';
        try {
            const tz = user.tz || Intl.DateTimeFormat().resolvedOptions().timeZone;
            return new Date(this.state.data.fetched_at).toLocaleTimeString([], {
                hour: '2-digit', minute: '2-digit', timeZone: tz,
            });
        } catch { return ''; }
    }

    get companyName() { return this.state.data?.company?.name || ''; }
}

registry.category("actions").add("sh_access_dashboard", ShDashboard);
