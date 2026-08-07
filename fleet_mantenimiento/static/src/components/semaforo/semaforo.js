/** @odoo-module **/

import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { xml } from "@odoo/owl"
import { registry } from "@web/core/registry";
import { loadCSS } from '@web/core/assets';

const {Component, onMounted, useState, useRef } = owl;

export class Semaforo extends Component {
    static template = xml`
        <div class="o_semaforo_display_widget_container">
            <div class="body">
                <div class="semaforo">
                    <div id="verde" t-ref="verde" class="luz verde"></div>
                    <div id="amarillo" t-ref="amarillo" class="luz amarillo"></div>
                    <div id="naranja" t-ref="naranja" class="luz naranja"></div>
                    <div id="rojo" t-ref="rojo" class="luz rojo"></div>
                    <div id="azul" t-ref="azul" class="luz azul"></div>
                </div>
            </div>
        </div>
    `;

    setup(){
        this.state = useState({
            color: "Sin aplicar",
        })
        this.divVerde = useRef("verde");
        this.divAmarillo = useRef("amarillo");
        this.divNaranja = useRef("naranja");
        this.divRojo = useRef("rojo");
        this.divAzul = useRef("azul");
        onMounted(this.mounted);
    }

    async mounted() {
        await loadCSS('/fleet_mantenimiento/static/src/css/style.css');
        this.state.color = this.fieldValue;
        this.cambiar(this.state.color);
    }

    static props = {
        ...standardFieldProps,
    };

    get fieldValue() {
        if (!this.props.record) return null;
        return this.props.record.data[this.props.name];
    }

    static supportedTypes = ["char", "text"];

    cambiar(color) {
        document.querySelectorAll('.luz').forEach(luz => {
            luz.classList.remove('activo');
        });
        if (color == 'Verde'){
            this.divVerde.el.classList.add('activo');
        }
        else if (color == 'Amarillo'){
            this.divAmarillo.el.classList.add('activo');
        }
        else if (color == 'Naranja'){
            this.divNaranja.el.classList.add('activo');
        }
        else if (color == 'Rojo'){
            this.divRojo.el.classList.add('activo');
        }
        else if (color == 'No aplica'){
            this.divAzul.el.classList.add('activo')
        }
    }

}
registry.category("fields").add("semaforo_display", {
    component: Semaforo,
    supportedTypes: Semaforo.supportedTypes,
});