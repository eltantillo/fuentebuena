/** @odoo-module **/

import { registry } from "@web/core/registry";
import { xml } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { DateTime } from "@web/core/l10n/dates";

const { Component, onWillStart } = owl;

export class RentaAuxilioTimeline extends Component {
    formatDate(dateStr) {
        if (!dateStr) return "-";
        const date = typeof dateStr === 'string' 
            ? DateTime.fromISO(dateStr.replace(' ', 'T')) 
            : dateStr;

        if (!date.isValid) return "-";
        return date.setZone("America/Mexico_City").toFormat("dd/MM/yyyy HH:mm");
    }

    static template = xml`
        <div class="fb_timeline_container">
            <div class="fb_timeline_line"></div>
            <t t-foreach="timelineRecords" t-as="item" t-key="item.resId">
                <div t-attf-class="fb_timeline_item #{item_index % 2 === 0 ? 'left' : 'right'}">
                    <div class="fb_timeline_card">
                        <div class="fb_timeline_title">
                            <i class="fa fa-car me-2"/>
                            <t t-esc="item.data.vehiculo_siniestro_id.display_name"/>
                        </div>
                        <div class="fb_timeline_content">
                            <div class="row">
                                <div class="col-lg-6 mb-2">
                                    <strong>Conductor</strong>
                                    <div><t t-esc="item.data.conductor_id.display_name"/></div>
                                </div>
                                <div class="col-lg-6 mb-2">
                                    <strong>Fecha inicio</strong>
                                    <div>
                                        <t t-esc="formatDate(item.data.fecha_inicio)"/>
                                    </div>
                                </div>
                                <div class="col-lg-6 mb-2">
                                    <strong>Días renta</strong>
                                    <div><t t-esc="item.data.dias_renta"/></div>
                                </div>
                                <div class="col-lg-6 mb-2">
                                    <strong>Fecha final</strong>
                                    <div>
                                        <t t-esc="formatDate(item.data.fecha_final)"/>
                                    </div>
                                </div>
                                <div class="col-lg-6 mb-2">
                                    <strong>Estado</strong>
                                    <div>
                                        <span t-if="item.data.estado === 'active'" class="badge bg-success text-white rounded-2">Activo</span>
                                        <span t-if="item.data.estado === 'finalizado'" class="badge bg-warning text-white rounded-2">Finalizado</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="fb_timeline_icon">
                        <i class="fa fa-car"/>
                    </div>
                </div>
            </t>
        </div>
    `;

    static props = {
        ...standardFieldProps,
    };

    static supportedTypes = ["one2many"];

    setup() {
        onWillStart(async () => {

        });
    }

    get timelineRecords() {
        if (!this.props.record) return [];
        const value = this.props.record.data[this.props.name];
        if (!value || !value.records) return [];
        return value.records;
    }
}

registry.category("fields").add("renta_auxilio_timeline", {
    component: RentaAuxilioTimeline,
    supportedTypes: RentaAuxilioTimeline.supportedTypes,
});