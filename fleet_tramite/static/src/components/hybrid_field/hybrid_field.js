/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUpdateProps, useState, xml } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { url } from "@web/core/utils/urls";

export class HybridField extends Component {
    static template = xml`
        <div class="o_field_pdfviewer d-flex flex-column w-100 m-0 p-0 align-items-stretch flex-grow-1" 
             style="min-width: 100% !important;"
             t-att-class="{ o_required_modifier: isRequired and !state.existe }">
            <t t-if="state.existe">
                <div class="o_pdfview_container position-relative w-100 d-flex flex-column flex-grow-1" style="min-height: 75vh; width: 70rem !important;">
                    <t t-if="state.esPdf">
                        <iframe t-att-src="state.previewUrl || fileUrl"
                                class="h-100 border-0 m-0 p-0 flex-grow-1"
                                style="min-height: 75vh; width: 100% !important; display: block;"/>
                    </t>
                    <t t-elif="state.esImagen">
                        <div class="w-100 bg-200 position-relative overflow-hidden" style="height: 75vh;">
                            <div class="position-absolute top-0 end-0 p-2 d-flex gap-1" style="z-index: 10;">
                                <button t-on-click="zoomIn" class="btn btn-sm btn-primary">+</button>
                                <button t-on-click="zoomOut" class="btn btn-sm btn-primary">-</button>
                                <button t-on-click="reset" class="btn btn-sm btn-secondary">⟳</button>
                            </div>
                            <div class="w-100 h-100 d-flex align-items-center justify-content-center"
                                t-on-mousedown="startDrag" t-on-mousemove="onDrag" t-on-mouseup="stopDrag" t-on-mouseleave="stopDrag">
                                <img t-att-src="state.previewUrl || fileUrl"
                                    t-att-style="'transform: translate(' + state.x + 'px,' + state.y + 'px) scale(' + state.zoom + '); transform-origin: center;'"
                                    style="cursor: grab; max-width: 100%; max-height: 75vh;"/>
                            </div>
                        </div>
                    </t>
                    <t t-else="">
                        <div class="o_select_file_button p-4 border rounded text-center w-100"
                             t-att-class="isRequired ? 'bg-light border-danger' : 'bg-light'">
                            <p class="mb-3 font-weight-bold" t-att-class="isRequired ? 'text-danger' : 'text-muted'">
                                <t t-if="isRequired">* El expediente es requerido obligatoriamente.</t>
                                <t t-else="">Archivo cargado en el expediente.</t>
                            </p>
                            <input type="file" t-on-change="subirArchivo" class="form-control d-inline-block w-auto"/>
                        </div>
                    </t>
                    <div class="position-absolute bottom-0 end-0 m-3" style="z-index: 100;">
                        <button class="btn btn-danger rounded-circle shadow" t-on-click="eliminarArchivo" title="Eliminar archivo" style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center;">
                            <span class="fa fa-trash"></span>
                        </button>
                    </div>
                </div>
            </t>
            <t t-else="">
                <div class="o_select_file_button p-4 border rounded text-center w-100"
                     t-att-class="isRequired ? 'bg-light border-danger' : 'bg-light'">
                    <p class="mb-3 font-weight-bold" t-att-class="isRequired ? 'text-danger' : 'text-muted'">
                        <t t-if="isRequired">* El expediente es requerido obligatoriamente.</t>
                        <t t-else="">No hay ningún documento cargado en el expediente.</t>
                    </p>
                    <input type="file" t-on-change="subirArchivo" class="form-control d-inline-block w-auto"/>
                </div>
            </t>
        </div>
    `;

    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.state = useState({
            esPdf: false,
            esImagen: false,
            existe: false,
            previewUrl: null,
            zoom: 1,
            x: 0,
            y: 0,
            dragging: false,
            startX: 0,
            startY: 0,
        });

        onMounted(() => this.detectarTipo());

        onWillUpdateProps((nextProps) => {
            const oldId = this.props.record.resId;
            const newId = nextProps.record.resId;
            if (newId && !oldId) {
                this.detectarTipo(nextProps);
            }
        });
    }

    // Getter dinámico para evaluar el estado requerido del campo sin romper OWL
    get isRequired() {
        const fieldInfo = this.props.record.fields[this.props.name];
        const activeField = this.props.record.activeFields?.[this.props.name];
        return !!(fieldInfo?.required || activeField?.required);
    }

    zoomIn = () => {
        this.state.zoom += 0.2;
    };

    zoomOut = () => {
        this.state.zoom = Math.max(0.2, this.state.zoom - 0.2);
    };

    reset = () => {
        this.state.zoom = 1;
        this.state.x = 0;
        this.state.y = 0;
    };

    startDrag = (ev) => {
        this.state.dragging = true;
        this.state.startX = ev.clientX - this.state.x;
        this.state.startY = ev.clientY - this.state.y;
    };

    onDrag = (ev) => {
        if (!this.state.dragging) return;

        this.state.x = ev.clientX - this.state.startX;
        this.state.y = ev.clientY - this.state.startY;
    };

    stopDrag = () => {
        this.state.dragging = false;
    };

    async detectarTipo(props = this.props) {
        const fieldValue = props.record.data[props.name];
        if (fieldValue && typeof fieldValue === 'string') {
            this.state.existe = true;
            if (fieldValue.startsWith('data:')) {
                this.state.previewUrl = fieldValue;
                this.state.esPdf = fieldValue.includes("application/pdf");
                this.state.esImagen = fieldValue.includes("image/");
                return;
            }
            if (fieldValue.startsWith('JVBERi')) {
                this.state.previewUrl = `data:application/pdf;base64,${fieldValue}`;
                this.state.esPdf = true;
                this.state.esImagen = false;
                return;
            } else if (fieldValue.length > 100) {
                this.state.previewUrl = `data:image/png;base64,${fieldValue}`;
                this.state.esPdf = false;
                this.state.esImagen = true;
                return;
            }
        }
        if (props.record.resId && typeof props.record.resId === 'number') {
            try {
                const res = await fetch(this.fileUrl, { method: "HEAD" });
                const contentType = res.headers.get("Content-Type") || "";
                const contentLength = res.headers.get("Content-Length");

                // Si la petición es correcta y no nos devuelve un HTML de error o vacío
                if (res.ok && contentLength !== "0" && !contentType.includes("html")) {
                    this.state.existe = true;
                    this.state.previewUrl = null; // Carga directo desde la fileUrl
                    this.state.esPdf = contentType.includes("pdf");
                    this.state.esImagen = contentType.startsWith("image/");
                    return;
                }
            } catch (e) {
                console.error("Error detectando tipo por URL:", e);
            }
        }
        this.resetState();
    }

    async subirArchivo(ev) {
        const file = ev.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (e) => {
            const dataUrl = e.target.result;
            const base64 = dataUrl.split(",")[1];

            try {
                await this.props.record.update({
                    [this.props.name]: base64
                });

                if (this.props.record.resId && typeof this.props.record.resId === 'number') {
                    await this.orm.call(
                        this.props.record.resModel,
                        "write_custom",
                        [[this.props.record.resId], { [this.props.name]: base64 }]
                    );
                }

                this.state.previewUrl = dataUrl;
                this.state.existe = true;
                this.state.esPdf = file.type.includes("pdf");
                this.state.esImagen = file.type.startsWith("image/");

            } catch (error) {
                console.error("Error en el proceso de subida:", error);
            }
        };
        reader.readAsDataURL(file);
    }

    async eliminarArchivo() {
        // En un One2many, delegamos el cambio al método relacional nativo update()
        // Odoo guardará/eliminará en BD automáticamente cuando se salve el formulario padre
        await this.props.record.update({
            [this.props.name]: false
        });

        this.resetState();
    }

    resetState() {
        this.state.existe = false;
        this.state.esPdf = false;
        this.state.esImagen = false;
        this.state.previewUrl = null;
    }

    get fileUrl() {
        if (!this.props.record.resId) return "";
        return url("/web/content", {
            model: this.props.record.resModel,
            field: this.props.name,
            id: this.props.record.resId,
            unique: this.props.record.data.write_date || Date.now(),
        });
    }

    static props = { ...standardFieldProps };
    static supportedTypes = ["binary"];
}

registry.category("fields").add("hybrid_field", {
    component: HybridField,
    supportedTypes: ["binary"],
});