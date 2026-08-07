/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';

const { Component, useState, onMounted, useRef } = owl;

class Posesion extends Component {
    setup() {
        this.orm = useService('orm');
        this.action = useService('action');
        this.notification = useService('notification');

        this.inputFoto1 = useRef("inputFoto1");
        this.inputFoto2 = useRef("inputFoto2");

        const context = this.props.action.context || {};
        this.resModel = context.active_model || 'gestion.caido';
        this.resId = context.active_id;
        this.new_stage = context.new_stage;
        this.vehiculo_id = context.vehiculo_id;
        this.type = context.type;

        this.state = useState({
            foto1: null,
            foto2: null,
            latitude: null,
            longitude: null,
            gpsStatus: "Obteniendo ubicación GPS...",
            isSaving: false,
        });
        console.log("Model: " + this.resModel)
        console.log("ID del mdoelo: "+ this.resId)

        onMounted(() => {
            this.obtenerGeolocalizacion();
        });
    }

    obtenerGeolocalizacion() {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.state.latitude = position.coords.latitude;
                    this.state.longitude = position.coords.longitude;
                    this.state.gpsStatus = `Ubicación obtenida (${this.state.latitude.toFixed(4)}, ${this.state.longitude.toFixed(4)})`;
                },
                (error) => {
                    console.error("Error al obtener GPS:", error);
                    this.state.gpsStatus = "No se pudo obtener el GPS. Asegúrate de dar permisos de ubicación.";
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        } else {
            this.state.gpsStatus = "Tu navegador no soporta Geolocalización.";
        }
    }

    async onFotoSelected(ev, fotoNum) {
        const file = ev.target.files[0];
        if (!file) return;

        const base64 = await this.fileToBase64(file);
        if (fotoNum === 1) {
            this.state.foto1 = base64;
        } else if (fotoNum === 2) {
            this.state.foto2 = base64;
        }
    }

    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result.split(',')[1]);
            reader.onerror = (error) => reject(error);
        });
    }

    async guardarEvidencia() {
        if (!this.state.foto1 || !this.state.foto2) {
            this.notification.add("Debes capturar ambas fotografías para continuar.", { type: "warning" });
            return;
        }
        this.state.isSaving = true;
        try {
            const coordenadas = `${this.state.latitude},${this.state.longitude}`;
            const name_etapa = await this.orm.searchRead(
                'gestion.caido.estado',
                [['id', '=', this.new_stage]],
                ['name']
            );
            const ubicacion = await this.orm.call(
                this.resModel,
                'obtener_ultima_ubi',
                [[this.resId]],
                {}
            );
            const updateValues = {
                estado_id: this.new_stage,
                evidencia_llave_posesion: this.state.foto1,
                evidencia_tarjeta_posesion: this.state.foto2,
                cordenadas_posesion: coordenadas,
                mostrar_page_posesion: false,
            };
            if (name_etapa.length > 0 && name_etapa[0].name === 'En posesión') {
                updateValues.mostrar_btn_retencion = false;
            }
            if (ubicacion){
                updateValues.ultima_ubi_vehiculo = ubicacion
            }
            if (this.type === 'posesion'){
                await this.orm.call(
                    this.resModel,
                    'registrar_evento',
                    [[this.resId],"Vehículo en posesión del gestor"],
                    {}
                );
                await this.orm.write(this.resModel, [this.resId], updateValues);
            }
            else if (this.type === 'recuperacion'){
                const updateValuesRec = {
                    estado_id: this.new_stage,
                    evidencia_recuperacion_uno: this.state.foto1,
                    evidencia_recuperacion_dos: this.state.foto2,
                    cordenadas_recuperacion: coordenadas,
                    ubi_vehiculo_recuperacion: ubicacion,
                };
                await this.orm.call(
                    this.resModel,
                    'termino_gestion',
                    [[this.resId]],
                    {}
                );
                await this.orm.write(this.resModel, [this.resId], updateValuesRec);

            }

            this.notification.add("Evidencia guardada y estado actualizado con éxito.", { type: "success" });
            this.action.doAction({ type: 'ir.actions.act_window_close' });
            window.location.reload();

        } catch (error) {
            console.error("Error guardando evidencias:", error);
            this.notification.add("Ocurrió un error al guardar la información.", { type: "danger" });
        } finally {
            this.state.isSaving = false;
        }
    }



    cancelar() {
        this.action.doAction({ type: 'ir.actions.act_window_close' });
    }
}

Posesion.template = 'gestion_caido.PosesionTemplate';
Posesion.components = {};

registry.category('actions').add('gc_posesion_posesion', Posesion);