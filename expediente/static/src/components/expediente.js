import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';
import { useSetupAction } from '@web/search/action_hook';
import { Component, useState, onWillStart, useRef } from "@odoo/owl";

const FLOTILLA_ID = 1;
const PAGE_SIZE = 250;

class Expediente extends Component {
    setup() {
        this.orm = useService('orm');
        this.notification = useService('notification');
        this.searchInputRef = useRef('searchInput');
        this.cambiarVista = this.cambiarVista.bind(this);
        this.goBack = this.goBack.bind(this);

        this.state = useState({
            estadoExpediente: null,
            searchTerm: "",
            tipoExpe: [],
            expeIncompletos: 0,
            expeCompletos: 0,
            isOpen: false,
            pdfUrl: null,
            title: "",
            totalVehiculos: 0,
            totalPages: 1,
            currentPage: 1,
            vehiculos: [],
            vehiculo: [],
            visibleList: [],
            isSearching: false,
            isLoading: true,
            plazas: [],
            tipoExpedientes: [],
            archivos: [],
            currentView: "vehiculos",
            idExpediente: 0,
            mostrarEstExpe: false,
            estadoFiltro: "",
            validacionMap: {},
            isDownloadingZip: false,
        });

        useSetupAction();
        onWillStart(async () => {
            let domain = [['flotilla_id','=', 1]]
            await this.loadVehiculos(domain);
            await this.loadPlazas();
            await this.loadExpedientes();
        });
    }

    async descargarArchivo(fileObj){
        const mime = fileObj.mimetype || 'application/pdf'
        this._descargarBase64(fileObj.data, fileObj.name || 'documento.pdf', mime);
    }

    _descargarBase64(base64Data, filename, mimetype) {
        const dataUrl = `data:${mimetype};base64,${base64Data}`;
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    openPreview = async (fileObj) => {
        if (!fileObj || !fileObj.data) return;

        if (this.state.pdfUrl) {
            URL.revokeObjectURL(this.state.pdfUrl);
            this.state.pdfUrl = null;
        }

        const mime = fileObj.mimetype || "application/pdf";
        const byteCharacters = atob(fileObj.data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: mime });

        this.state.pdfUrl = URL.createObjectURL(blob);
        this.state.title = fileObj.name || "Vista previa";
        this.state.isOpen = true;
    };

    async closeModal() {
        if (this.state.pdfUrl) {
            URL.revokeObjectURL(this.state.pdfUrl);
        }
        this.state.pdfUrl = null;
        this.state.isOpen = false;
    }

    async loadVehiculos(domain) {
        try {
            const vehiculos = await this.orm.searchRead(
                'fleet.vehicle',
                domain,
                ['id', 'vin_sn','plaza_id','license_plate']
            );

            this.state.vehiculos = vehiculos.map(v => ({
                ...v,
                vinLower: String(v.vin_sn || "").toLowerCase(),
            }));
            this.state.totalVehiculos = vehiculos.length;
            this.state.totalPages = Math.max(1, Math.ceil(vehiculos.length / PAGE_SIZE));

            this.goToPage(1);
        } catch (error) {
            this.notification.add("No se pudo cargar el listado de vehículos", {
                type: "danger",
            });
        } finally {
            this.state.isLoading = false;
        }
    }

    async obtener_archivos(vehiculo_id){
        return this.orm.call(
            'fleet.vehicle','get_expediente',[vehiculo_id],{}
        )
    }

    async obtener_archivos_tipo(vehiculo_id){
        return this.orm.call(
            'fleet.vehicle','get_expediente_type',[this.state.idExpediente,vehiculo_id],{}
        )
    }

    async cambiarVista(vehiculo){
        console.log("=============================0")
        console.log(vehiculo)
        this.state.vehiculo = vehiculo
        console.log(vehiculo['id'])
        if (this.state.idExpediente){
            this.state.archivos = await this.obtener_archivos_tipo(vehiculo['id'])
        }
        else {
            this.state.archivos = await this.obtener_archivos(vehiculo['id'])
        }
        console.log(this.state.archivos)
        this.state.currentView = "archivos"
    }


    goBack(){
        this.state.currentView = "vehiculos"
    }

    async loadPlazas(){
        try{
            this.state.plazas  = await this.orm.searchRead(
                'fleet.customer.plaza',
                [],
                ['id', 'name']
            );

        }catch (error) {
            this.notification.add("No se pudo cargar el listado de vehículos", {
                type: "danger",
            });
        }
    }

    async loadExpedientes(){
        try{
            this.state.tipoExpedientes  = await this.orm.searchRead(
                'expediente.tipo',
                [],
                ['id', 'name']
            );

        }catch (error) {
            this.notification.add("No se pudo cargar el listado de vehículos", {
                type: "danger",
            });
        }
    }

    async onChangeExpediente(ev) {
        this.state.idExpediente = parseInt(ev.target.value) || 0;
        this.state.estadoFiltro = "";
        await this._recomputeValidacion();
        this._refreshVisibleList();
    }

    async _recomputeValidacion() {
        if (!this.state.idExpediente) {
            this.state.mostrarEstExpe = false;
            this.state.tipoExpe = [];
            this.state.validacionMap = {};
            this.state.expeIncompletos = [];
            this.state.expeCompletos = [];
            return;
        }
        const vehicleIds = this.state.vehiculos.map(vehiculo => vehiculo.id);
        this.state.tipoExpe = await this.orm.call(
            'fleet.vehicle','return_validacion_expe',[vehicleIds, this.state.idExpediente],{}
        )
        this.state.mostrarEstExpe = true
        this.separarExpediente()
    }

    separarExpediente(){
        let expedientes = this.state.tipoExpe
        this.state.expeIncompletos = expedientes.filter(item => item.expediente === 'incompleto')
        expedientes = this.state.tipoExpe
        this.state.expeCompletos = expedientes.filter(item => item.expediente === 'completo')
        console.log("========Incompletos==========")
        console.log(this.state.expeIncompletos.length)
        console.log(this.state.expeIncompletos)
        console.log("========Completos==========")
        console.log(this.state.expeCompletos.length)
        console.log(this.state.expeCompletos)
        const vinToId = {};
        for (const v of this.state.vehiculos) {
            vinToId[v.vin_sn] = v.id;
        }
        const validacionMap = {};
        for (const item of this.state.tipoExpe) {
            const vid = vinToId[item.vehiculo];
            if (vid !== undefined) {
                validacionMap[vid] = { estado: item.expediente, faltantes: item.faltantes };
            }
        }
        this.state.validacionMap = validacionMap;
    }

    _refreshVisibleList() {
        const hayFiltroActivo = this.state.isSearching || !!this.state.estadoFiltro;

        if (!hayFiltroActivo) {
            this.goToPage(this.state.currentPage);
            return;
        }

        let lista = this.state.vehiculos;
        if (this.state.isSearching && this.state.searchTerm) {
            lista = lista.filter(v => v.vinLower.includes(this.state.searchTerm));
        }
        if (this.state.estadoFiltro) {
            lista = lista.filter(v => {
                const info = this.state.validacionMap[v.id];
                return info && info.estado === this.state.estadoFiltro;
            });
        }
        this.state.visibleList = lista;
    }

    onChangeEstadoExpe(ev) {
        this.state.estadoFiltro = ev.target.value || "";
        this._refreshVisibleList();
    }

    async onClickEstadoBadge(estado) {
        console.log("Valor del estado de onClickEstadoBadge")
        console.log(estado)
        if (!this.state.mostrarEstExpe) {
            this.notification.add("Primero selecciona un tipo de expediente.", { type: "warning" });
            return;
        }
        this.state.estadoFiltro = estado;
        this._refreshVisibleList();
        await this.descargarExcelFaltantes(estado);
    }

    verTodos() {
        this.state.estadoFiltro = "";
        this._refreshVisibleList();
    }

    async descargarZip() {
        if (!this.state.vehiculo || !this.state.vehiculo.id) return;
        this.state.isDownloadingZip = true;
        try {
            const zipDoc = await this.orm.call(
                'fleet.vehicle', 'get_zip_expediente', [this.state.vehiculo.id, this.state.idExpediente], {}
            );
            if (!zipDoc) {
                this.notification.add("No hay documentos disponibles para descargar.", { type: "warning" });
                return;
            }
            this._descargarBase64(zipDoc.data, zipDoc.name, zipDoc.mimetype);
        } catch (error) {
            this.notification.add("No se pudo generar el ZIP del expediente", { type: "danger" });
        } finally {
            this.state.isDownloadingZip = false;
        }
    }

    async descargarExcelFaltantes(estado) {
        if (!this.state.idExpediente) {
            this.notification.add("Primero selecciona un tipo de expediente.", { type: "warning" });
            return;
        }
        try {
            const vehicleIds = this.state.vehiculos.map(vehiculo => vehiculo.id);
            const excelDoc = await this.orm.call(
                'fleet.vehicle', 'get_faltantes_excel',
                [vehicleIds, this.state.idExpediente, estado || false], {}
            );
            if (!excelDoc) {
                this.notification.add("No hay resultados para exportar.", { type: "warning" });
                return;
            }
            this._descargarBase64(excelDoc.data, excelDoc.name, excelDoc.mimetype);
        } catch (error) {
            this.notification.add("No se pudo generar el Excel de faltantes", { type: "danger" });
        }
    }

    async on_change_plaza(ev) {
        let domain = []
        const plaza_id = parseInt(ev.target.value);
        if (plaza_id){
            domain = [
                ['flotilla_id', '=', 1],
                ['plaza_id', '=', plaza_id]
            ];
        }
        else {
            domain = [['flotilla_id', '=', 1]]
        }
        await this.loadVehiculos(domain);
        this.state.estadoFiltro = "";
        await this._recomputeValidacion();
        this._refreshVisibleList();
    }

    goToPage(page) {
        const clamped = Math.min(Math.max(1, page), this.state.totalPages);
        this.state.currentPage = clamped;

        const start = (clamped - 1) * PAGE_SIZE;
        this.state.visibleList = this.state.vehiculos.slice(start, start + PAGE_SIZE);
    }

    nextPage() {
        this.goToPage(this.state.currentPage + 1);
    }

    prevPage() {
        this.goToPage(this.state.currentPage - 1);
    }

    _onSearchKeydown(ev) {
        if (ev.key === 'Enter') {
            this.executeSearch(ev.target.value);
        }
    }

    _onSearchClick() {
        this.executeSearch(this.searchInputRef.el.value);
    }

    executeSearch(term) {
        const cleanTerm = (term || "").trim().toLowerCase();
        this.state.searchTerm = cleanTerm;

        if (!cleanTerm) {
            this.clearSearch();
            return;
        }

        this.state.isSearching = true;
        this._refreshVisibleList();
    }

    clearSearch() {
        this.state.searchTerm = "";
        this.state.isSearching = false;
        if (this.searchInputRef.el) {
            this.searchInputRef.el.value = "";
        }
        this.state.currentPage = 1;
        this._refreshVisibleList();
    }
}

Expediente.template = 'expediente.main';
Expediente.components = {};

registry.category('actions').add('expediente', Expediente);