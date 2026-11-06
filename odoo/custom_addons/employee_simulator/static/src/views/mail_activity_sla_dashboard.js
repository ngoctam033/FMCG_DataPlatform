/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { Component, onWillStart, onWillUpdateProps } from "@odoo/owl";

const { DateTime } = luxon;

export class EmployeeActivitySlaDashboard extends Component {
    static template = "employee_simulator.EmployeeActivitySlaDashboard";
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
        const today = DateTime.local().toISODate();
        const context = { ...props.list.context, active_test: false };
        const count = (extraDomain = []) =>
            this.orm.searchCount("mail.activity", extraDomain, { context });

        const [total, open, overdue, dueToday, planned, done, doneToday, repeated] = await Promise.all([
            count(),
            count([["active", "=", true]]),
            count([["active", "=", true], ["date_deadline", "<", today]]),
            count([["active", "=", true], ["date_deadline", "=", today]]),
            count([["active", "=", true], ["date_deadline", ">", today]]),
            count([["active", "=", false]]),
            count([["active", "=", false], ["date_done", "=", today]]),
            count([["is_repeated_issue", "=", true]]),
        ]);

        this.dashboardData = { total, open, overdue, dueToday, planned, done, doneToday, repeated };
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

export class EmployeeActivitySlaListRenderer extends ListRenderer {
    static template = "employee_simulator.EmployeeActivitySlaListRenderer";
    static components = {
        ...ListRenderer.components,
        EmployeeActivitySlaDashboard,
    };
}

export const employeeActivitySlaDashboardListView = {
    ...listView,
    Renderer: EmployeeActivitySlaListRenderer,
};

registry.category("views").add(
    "employee_activity_sla_dashboard_list",
    employeeActivitySlaDashboardListView
);
