/** @odoo-module **/

import { user } from '@web/core/user';
import { registry } from '@web/core/registry';
import { rpc } from '@web/core/network/rpc';
import { session } from '@web/session'
import { useService } from '@web/core/utils/hooks';
import { useSetupAction } from '@web/search/action_hook';
import { loadJS } from '@web/core/assets';
import { Dialog } from '@web/core/dialog/dialog';

const {Component, useState, onWillStart, onWillUnmount, onMounted, useRef} = owl;

class Recepcion extends Component {
    static template = 'fleet_recepcion.recepcion'

    setup(){
        this.orm = useService('orm');
        this.action = useService('action');
        this.rpc = rpc;
        this.modalRef = useRef("");
        this.modalInstance = null;
        this.dialogService = useService('dialog');
        
        this.state = useState({
            vehiculos: [],
            dataVehiculo: [],
            productos: [],
            currentView: 'fleet_recepcion_recepcion',
            modelos_vehiculo: [],
            vehiculo: {
                model_id: "", 
                vin_sn: "",
                numero_economico: "",
                producto_id: "",
                factura: "",
                model_year: "",
            },
            recepcion: {
                fecha_recepcion: "",
                condicion_vehiculo_id: "",
                lugar_recepcion_id: "",
                permiso_provisional: "",
                vehiculo_id: "",
                exterior_trasero_cajuela: "",
                exterior_trasero_calavera: "",
                exterior_trasero_defensa: "",
                exterior_trasero_llantaref_gato: "",
                exterior_trasero_refherramienta: "",
                exterior_trasero_portaplaca: ""
            },
            modalFrontal: "",
            modalTrasero: "",
            modalLatDerecho: "",
            modalLatIzquierdo: "",
            modalIntFrontal: "",
            modalInteriores: "",
            modalInfoVehiculo: "",
            modalNoVehiculo: "",
            modalVehiculoCreado: "",
        });

        useSetupAction();
        onWillStart(this.willStart);
        onMounted(this.mounted);
        onWillUnmount(this.willUnmount);

    }

    async loadLibs(){
        loadJS('/fleet_recepcion/static/libs/bootstrap.bundle.min.js');
    }

    async willStart() {
        await this.loadLibs();
        this.state.vehiculos = await this.orm.searchRead(
            'fleet.vehicle',
            [],
            ['id','vin_sn','numero_economico']
        );
        this.state.modelos_vehiculo = await this.orm.searchRead(
            'fleet.vehicle.model',
            [],
            []
        );
        this.state.productos = await this.orm.searchRead(
            'fleet.customer.producto',
            [],
            []
        )
        console.log(this.state.vehiculos)
    }

    async mounted() {
        console.log("Hola mundo");
    }

    async willUnmount() {
        /**
         *
        */
    }

    on_change_faro(ev){
        this.rem_add_clase_input("faro_observacion", ev.target.value);
    }

    on_change_cofre(ev){
        this.rem_add_clase_input("cofre_observacion", ev.target.value);
    }

    on_change_porta_placa_frontal(ev){
        this.rem_add_clase_input("porta_placa_frontal_observacion", ev.target.value);
    }

    on_change_taponnivel(ev){
        this.rem_add_clase_input("taponnivel_observacion", ev.target.value);
    }

    on_change_varilla_aceite(ev){
        this.rem_add_clase_input("varilla_aceite_observacion", ev.target.value);
    }

    on_change_nivel_aceite(ev){
        this.rem_add_clase_input_especial("nivel_aceite_observacion", ev.target.value);
    }

    on_change_anticongelante(ev){
        this.rem_add_clase_input_especial("anticongelante_observacion", ev.target.value);
    }

    on_change_liquido_frenos(ev){
        this.rem_add_clase_input_especial("liquido_frenos_observacion", ev.target.value);
    }

    on_change_facia_frontal(ev){
        this.rem_add_clase_input("facia_frontal_observacion", ev.target.value);
    }

    on_change_limpiador_frontal(ev){
        this.rem_add_clase_input("limpiador_frontal_observacion", ev.target.value);
    }

    on_change_antena(ev){
        this.rem_add_clase_input("antena_observacion", ev.target.value);
    }

    on_change_cajuela(ev){
        this.rem_add_clase_input("cajuela_observacion", ev.target.value);
    }

    on_change_calavera(ev){
        this.rem_add_clase_input("calavera_observacion", ev.target.value);
    }

    on_change_defensa(ev){
        this.rem_add_clase_input("defensa_observacion", ev.target.value);
    }

    on_change_llantaref_gato(ev){
        this.rem_add_clase_input("llanta_gato_observacion", ev.target.value);
    }

    on_change_refherramienta(ev){
        this.rem_add_clase_input("ref_herramienta_observacion", ev.target.value);
    }

    on_change_portaplaca_trasera(ev){
        this.rem_add_clase_input("portaplaca_trasera_observacion", ev.target.value);
    }

    on_change_espejo_izquierdo(ev){
        this.rem_add_clase_input("espejo_izquierdo_observacion", ev.target.value);
    }

    on_change_costado_izquierdo(ev){
        this.rem_add_clase_input("costado_izquierdo_observacion", ev.target.value);
    }

    on_change_tapon_gasolina(ev){
        this.rem_add_clase_input("tapon_gasolina_observacion", ev.target.value);
    }

    on_change_espejo_derecho(ev){
        this.rem_add_clase_input("espejo_derecho_observacion", ev.target.value);
    }

    on_change_costado_derecho(ev){
        this.rem_add_clase_input("costado_derecho_observacion", ev.target.value);
    }

    on_change_interiores(ev){
        this.rem_add_clase_input("interiores_observacion", ev.target.value);
    }

    on_change_tapetes(ev){
        this.rem_add_clase_input("tapetes_observacion", ev.target.value);
    }

    on_change_vidrios(ev){
        this.rem_add_clase_input("vidrios_observacion", ev.target.value);
    }

    on_change_birlos(ev){
        this.rem_add_clase_input("birlos_observacion", ev.target.value);
    }

    on_change_tablero(ev){
        this.rem_add_clase_input("tablero_observacion", ev.target.value);
    }

    on_change_estereo(ev){
        this.rem_add_clase_input("estereo_observacion", ev.target.value);
    }

    on_change_clima(ev){
        this.rem_add_clase_input("clima_observacion", ev.target.value);
    }

    on_change_espejo_retrovisor(ev){
        this.rem_add_clase_input("espejo_observacion", ev.target.value);
    }

    rem_add_clase_input(nom_input,valor){
        var input = document.getElementById(nom_input);
        console.log(valor);
        if (valor === "Bueno"){
            input.classList.add("input-hidden");
            input.required = false;
        }
        else if (valor === "Malo"){
            input.classList.remove("input-hidden");
            input.required = true;
        }
        else {
            console.log("no entra a valor");
        }
    }

    rem_add_clase_input_especial(nom_input,valor){
        var input = document.getElementById(nom_input);
        console.log(valor);
        if (valor === "Optimo"){
            input.classList.add("input-hidden");
            input.required = false;
        }
        else if (valor === "Medio"){
            input.classList.remove("input-hidden");
            input.required = true;
        }
        else if( valor === "Bajo"){
            input.classList.remove("input-hidden");
            input.required = true;
        }
        else {
            console.log("no entra a valor")
        }
    }

    buscar(campo) {
        const input = document.getElementById("input_busqueda");
        const vehiculos = this.state.vehiculos;
        const resul = vehiculos.filter(v => v[`${campo}`] === input.value);
        if (resul.length > 0) {
            this.state.dataVehiculo = resul[0]; 
            this.showModal("modal_info_vehiculo","modalInfoVehiculo");      
        } else {
            this.showModal("modal_vehiculo_no_encontrado","modalNoVehiculo");
        }
    }

    showModal(modal_id,state_modal){
        var modalEl = document.getElementById(modal_id);
        this.state[`${state_modal}`] = bootstrap.Modal.getOrCreateInstance(modalEl);
        this.state[`${state_modal}`].show();
    }

    busqueda_vehiculo(){
        let input_vin = document.getElementById("radio_vin");
        let input_nun_economico = document.getElementById("radio_numero_economico");
        if (input_vin.checked){
            this.buscar("vin_sn");
        }
        else if(input_nun_economico.checked ){
            this.buscar("numero_economico");
        }
        else {
            console.log("Seleccione mediante que atributo buscar");
        }
    }

    crearVehiculoView() {
        this.state.modalNoVehiculo.hide();
        this.state.currentView = 'fleet_recepcion_alta';
    }

    async crearVehiculo(){
        try {
            const vehiculo = await this.orm.create('fleet.vehicle', [{
                model_id: parseInt(this.state.vehiculo.model_id),
                vin_sn: this.state.vehiculo.vin_sn,
                numero_economico: this.state.vehiculo.numero_economico,
                producto_id: parseInt(this.state.vehiculo.producto_id),
                factura: this.state.vehiculo.factura,
                model_year: this.state.vehiculo.model_year
            }]);
            this.showModal("modal_vehiculo_creado","modalVehiculoCreado");
            this.state.dataVehiculo = this.state.vehiculo;
        }
        catch{
            console.log("No se ejecutaron correctamente las acciones");
        }
    }

    async evaluar(){
        this.state.modalInfoVehiculo.hide();
        this.state.currentView = "fleet_recepcion_valorar";
    }

    async continuarRecepcion(){
        this.state.modalVehiculoCreado.hide();
         this.state.currentView = "fleet_recepcion_valorar";
    }

    listener_foto(){
        const input = document.getElementById("fotoInput");
        const preview = document.getElementById("preview");
        const uploadLabel = document.getElementById("uploadLabel");

        input.addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (file) {
            preview.src = URL.createObjectURL(file);
            preview.style.display = "block";
            uploadLabel.style.display = "none";
        }
        if (input.files.length > 0){
                let div = document.getElementById("uploadBox");
                div.style.borderColor = "green";
            }
        });
    }

    showModalFrontal(){
        this.showModal("modalFrontal","modalFrontal");      
    }

    showModalTrasero(){
        this.showModal("modalTrasero","modalTrasero");     
        this.listener_foto(); 
    }

    showModalIzquierdo(){
        this.showModal("modallatIzquierdo","modalLatIzquierdo");
    }

    showModalDerecho(){
        this.showModal("modallatDerecho","modalLatDerecho");
    }

    showInteriorFrontal(){
        this.showModal("modalintFrontal","modalIntFrontal");
    }

    showInteriores(){
        this.showModal("modalinteriores","modalInteriores");
    }

    confirmar_frontal(){
        this.state.modalFrontal.hide();
        this.style_confirm("btnFrontal","iconFrontal");   
    }

    confirmar_trasero(){
        this.state.modalTrasero.hide();
        this.style_confirm("btnTrasero","iconTrasero");   
        this.confirmarcoche();
    }

    confirmar_lat_izquierdo(){
        this.state.modalLatIzquierdo.hide();
        this.style_confirm("btnlatIzquierdo","iconlatIzquierdo");   
    }

    confirmar_lat_derecho(){
        this.state.modalLatDerecho.hide();
        this.style_confirm("btnlatDerecho","iconlatDerecho");   
    }

    confirmar_interior_frontal(){
        this.state.modalIntFrontal.hide();
        this.style_confirm("btninteriorFrontal","iconintFrontal");
    }

    confirmar_interiores(){
        this.state.modalInteriores.hide();
        this.style_confirm("btninteriores","iconinteriores");
    }

    style_confirm(btn_id,icon_id){
        var btn = document.getElementById(btn_id);
        btn.style.backgroundColor = "green";
        var icon = document.getElementById(icon_id);
        icon.classList.remove("fa-exclamation");   
        icon.classList.add("fa-check"); 
    }

    async confirmarcoche(){
        const vehiculo = this.state.vehiculos.filter(v => v["vin_sn"] === this.state.dataVehiculo.vin_sn);
        let recepcion = this.orm.create('fleet.recepcion', [{
            vehiculo_id: vehiculo[0].id
        }]);
    }

    submitFormValidate(event) {
        event.preventDefault()
        event.stopPropagation()
        const form = event.target;
        if (form.checkValidity()) {
            if (form.id === 'form_lateral_derecho') {
                this.confirmar_lat_derecho();
            }
            else if (form.id === 'form_interiores'){
                this.confirmar_interiores();
            }
            else if (form.id === 'form_interior_frontal'){
                this.confirmar_interior_frontal();
            }
            else if (form.id === 'form_lateral_izquierdo'){
                this.confirmar_lat_izquierdo();
            }
            else if(form.id === 'form_trasero'){
                this.confirmar_trasero();
            }
            else if (form.id === 'form_frontal'){
                this.confirmar_frontal();
            }
        } else {
            let inputImage = document.getElementById("fotoInput");
            if (inputImage.files.length <= 0){
                let div = document.getElementById("uploadBox");
                div.style.borderColor = "red";
            }
            form.classList.add('was-validated');
            form.classList.add('is-invalid');
        }
    }

}
Recepcion.components = {};

registry.category('actions').add('fleet_recepcion_recepcion', Recepcion);