 /** @odoo-module **/

import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { xml } from "@odoo/owl"
import { registry } from "@web/core/registry";

const {Component, onMounted, useState} = owl;

export class MyGoogleMapWidget extends Component {
    static template = xml`
        <div class="o_google_map_widget_container">
            <t t-if="state.coordenadas">
                <iframe
                    t-att-src="googleMapsUrl"
                    width="100%"
                    height="400"
                    frameborder="0"
                    style="border:0"
                    allowfullscreen=""
                    loading="lazy"
                    referrerpolicy="no-referrer-when-downgrade">
                </iframe>
            </t>
            <t t-else="">
                <div class="text-muted">No hay coordenadas disponibles para mostrar el mapa.</div>
            </t>
        </div>
    `;

    setup(){
        this.state = useState({
            coordenadas: false,
        })
        onMounted(this.mounted);
    }

    mounted() {
        this.state.coordenadas = this.fieldValue;
    }

    static props = {
        ...standardFieldProps,
    };

    get fieldValue() {
        if (!this.props.record) return null;
        return this.props.record.data[this.props.name];
    }

    static supportedTypes = ["char", "text"];

    get googleMapsUrl() {
        const coordinates = this.state.coordenadas;
        if (!coordinates) {
            return "";
        }
        return `https://maps.google.com/maps?q=${coordinates}&z=15&output=embed`;
    }
}
registry.category("fields").add("google_map_display", {
    component: MyGoogleMapWidget,
    supportedTypes: MyGoogleMapWidget.supportedTypes,
});