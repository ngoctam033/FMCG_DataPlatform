/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { Component, onWillStart, onWillUpdateProps } from "@odoo/owl";

const { DateTime } = luxon;

const OPEN_DOMAIN = [["state", "not in", ["done", "cancel"]]];

export class StockPickingOperationalDashboard extends Component {
    static template = "fmcg_stock_picking_dashboard.StockPickingOperationalDashboard";
    static props = {
        list: Object,
    };

    setup() {
        this.orm = useService("orm");
        this.dashboardData = {};

        onWillStart(() => this.loadDashboardData(this.props));
        onWillUpdateProps((nextProps) => this.loadDashboardData(nextProps));
    }

    async loadDashboardData(props) {
        const now = DateTime.local().toUTC().toFormat("yyyy-MM-dd HH:mm:ss");
        const context = { ...props.list.context };
        const count = (extraDomain = []) =>
            this.orm.searchCount("stock.picking", [...OPEN_DOMAIN, ...extraDomain], { context });

        const [
            total,
            draft,
            waitingOperation,
            waitingStock,
            ready,
            lateAvailability,
            overdue,
            backorder,
            activityOverdue,
        ] = await Promise.all([
            count(),
            count([["state", "=", "draft"]]),
            count([["state", "=", "waiting"]]),
            count([["state", "=", "confirmed"]]),
            count([["state", "=", "assigned"]]),
            count([
                ["state", "in", ["confirmed", "waiting"]],
                ["products_availability_state", "=", "late"],
            ]),
            count([["scheduled_date", "<", now]]),
            count([["backorder_id", "!=", false]]),
            count([["activity_state", "=", "overdue"]]),
        ]);

        this.dashboardData = {
            total,
            draft,
            waitingOperation,
            waitingStock,
            ready,
            lateAvailability,
            overdue,
            backorder,
            activityOverdue,
        };
    }

    setSearchContext(ev) {
        const filterNames = ev.currentTarget.dataset.filters.split(",").filter(Boolean);
        const searchItems = this.env.searchModel.getSearchItems((item) =>
            filterNames.includes(item.name)
        );

        this.env.searchModel.query = [];
        for (const item of searchItems) {
            this.env.searchModel.toggleSearchItem(item.id);
        }
    }
}

export class StockPickingOperationalListRenderer extends ListRenderer {
    static template = "fmcg_stock_picking_dashboard.StockPickingOperationalListRenderer";
    static components = {
        ...ListRenderer.components,
        StockPickingOperationalDashboard,
    };
}

export const stockPickingOperationalDashboardListView = {
    ...listView,
    Renderer: StockPickingOperationalListRenderer,
};

registry.category("views").add(
    "fmcg_stock_picking_dashboard_list",
    stockPickingOperationalDashboardListView
);
