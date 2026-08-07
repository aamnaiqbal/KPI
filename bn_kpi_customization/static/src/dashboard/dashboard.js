/** @odoo-module **/

import { Component } from "@odoo/owl";
import {registry} from "@web/core/registry";

export class Dashboard extends Component {}

Dashboard.template = "bn_kpi_customization.Dashboard";

registry.category("actions").add("kpi_dashboard", Dashboard);