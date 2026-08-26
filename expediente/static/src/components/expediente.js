import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';
import { useSetupAction } from '@web/search/action_hook';
import { Component, useState, onWillStart, useRef } from "@odoo/owl";

const PAGE_SIZE = 25;

class Expediente extends Component {
    setup() {
        this.orm = useService('orm');
        this.notification = useService('notification');
        this.mainRef = useRef('mainContainer');

        this.state = useState({
            currentPage: 1,
            vehiculos: [],
            filtrosActivos: [],
            VehiculosExpediente: [],
            expeIncompletos: [],
            expeCompletos: [],
            expeIncompletosInt: 0,
            expeCompletosInt: 0,
            plazas: [],
            tipoExpedientes: [],
            documento_filter: [],
            vehiculoSeleccionado: null,
            idExpediente: null,
            selectedPlaza: null,
            selectedDocumento: null,
            searchQuery: '',
            isLoading: true,
            archivosVehiculo: null,
            isLoadingArchivos: false,
            isDownloadingZip: false,
            isOpen: false,
            pdfUrl: null,
            title: "",
        });

        useSetupAction();

        onWillStart(async () => {
            await Promise.all([
                this.loadPlazas(),
                this.loadDocumentos(),
                this.loadExpedientesTypo(),
                this.loadVehiculos()
            ]);
            await this.initExpedientePrincipal();
        });
    }

    scrollToTop() {
        if (this.mainRef.el) {
            this.mainRef.el.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    _mapStateToMotivo(estado) {
        const map = {
            'vigente': 'vigente',
            'falta subir': 'falta subir',
            'vencido': 'vencido',
            'sin registro': 'sin registro'
        };
        return map[estado] || estado;
    }

    _getTodosDocumentosVehiculo(vehiculo) {
        if (!vehiculo) return [];

        const faltantes = (vehiculo.faltantes || []).map(f => {
            const nombre = typeof f === 'object' ? (f.faltante || f.completo || '') : f;
            const motivo = typeof f === 'object' ? (f.motivo || 'falta subir') : 'falta subir';
            return { faltante: nombre, motivo: motivo };
        });

        const completos = (vehiculo.completos || []).map(c => {
            const nombre = typeof c === 'object' ? (c.completo || c.faltante || '') : c;
            return { faltante: nombre, motivo: 'vigente' };
        });

        return [...faltantes, ...completos];
    }

    getDocumentosFiltrados(vehiculo) {
        let todosDocs = this._getTodosDocumentosVehiculo(vehiculo);
        if (this.state.selectedDocumento) {
            const docFilter = this.state.selectedDocumento.trim().toLowerCase();
            todosDocs = todosDocs.filter(
                doc => (doc.faltante || '').trim().toLowerCase() === docFilter
            );
        }

        if (this.state.filtrosActivos.length > 0) {
            const motivosActivos = this.state.filtrosActivos.map(f => this._mapStateToMotivo(f));
            todosDocs = todosDocs.filter(doc => motivosActivos.includes(doc.motivo));
        }

        return todosDocs;
    }

    get filteredVehiculos() {
        let list = this.state.VehiculosExpediente;

        if (this.state.searchQuery.trim()) {
            const query = this.state.searchQuery.trim().toLowerCase();
            list = list.filter(v => {
                const vin = (v.vehiculo || '').toLowerCase();
                const placa = (v.license_plate || '').toLowerCase();
                return vin.includes(query) || placa.includes(query);
            });
        }

        if (this.state.selectedDocumento || this.state.filtrosActivos.length > 0) {
            list = list.filter(v => this.getDocumentosFiltrados(v).length > 0);
        }

        return list;
    }

    get totalPages() {
        return Math.ceil(this.filteredVehiculos.length / PAGE_SIZE) || 1;
    }

    get paginatedList() {
        const inicio = (this.state.currentPage - 1) * PAGE_SIZE;
        return this.filteredVehiculos.slice(inicio, inicio + PAGE_SIZE);
    }

    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.state.currentPage = page;
            this.scrollToTop();
        }
    }

    nextPage() { this.goToPage(this.state.currentPage + 1); }
    prevPage() { this.goToPage(this.state.currentPage - 1); }

    _onSearchInput(ev) {
        this.state.searchQuery = ev.target.value;
        this.state.currentPage = 1;
    }

    onChangeDocumento(ev) {
        console.log("Dentro de proceso change documento")
        console.log(this.state.VehiculosExpediente);
        const val = ev.target.value;
        console.log("Valor de val: " + val)
        this.state.selectedDocumento = val === "todos" ? null : val;
        this.state.currentPage = 1;
        if (val !== 'todos'){
            const data = this.contarEstadoPorArchivo(this.state.VehiculosExpediente,val)
            this.state.expeCompletosInt = data['completos']
            this.state.expeIncompletosInt = data['incompletos']
        }else {
            this.state.expeCompletosInt = this.state.expeCompletos.length
            this.state.expeIncompletosInt = this.state.expeIncompletos.length
        }
    }

    contarEstadoPorArchivo(listaCoches, nombreArchivo) {
        let completos = 0;
        let incompletos = 0;

        for (let i = 0; i < listaCoches.length; i++) {
            const coche = listaCoches[i];
            if (coche.completos && coche.completos.some(c => c.completo === nombreArchivo)) {
                completos++;
            }
            else if (coche.faltantes && coche.faltantes.some(f => f.faltante === nombreArchivo)) {
                incompletos++;
            }
        }

        let data = {
            archivo: nombreArchivo,
            completos: completos,
            incompletos: incompletos,
            totalEvaluados: completos + incompletos
        };
        console.log(data)
        return data
    }

    toggleFiltro(estado) {
        const idx = this.state.filtrosActivos.indexOf(estado);
        if (idx === -1) {
            this.state.filtrosActivos.push(estado);
        } else {
            this.state.filtrosActivos.splice(idx, 1);
        }
        this.state.currentPage = 1;
    }

    async loadVehiculos(domain = [['flotilla_id', '=', 1]]) {
        try {
            this.state.isLoading = true;
            this.state.vehiculos = await this.orm.searchRead(
                'fleet.vehicle',
                domain,
                ['id', 'vin_sn', 'plaza_id', 'license_plate']
            );
        } catch (error) {
            console.error("Error al cargar vehículos:", error);
            this.notification.add("No se pudo cargar el listado de vehículos", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    async loadPlazas() {
        try {
            this.state.plazas = await this.orm.searchRead('fleet.customer.plaza', [], ['id', 'name']);
        } catch (error) {
            this.notification.add("No se pudo cargar el listado de plazas", { type: "danger" });
        }
    }

    async loadDocumentos() {
        try {
            this.state.documento_filter = await this.orm.call('expediente.tipo', 'return_documents', [], {});
        } catch (error) {
            this.notification.add("No se pudo cargar el listado de Documentos", { type: "danger" });
        }
    }

    async loadExpedientesTypo() {
        try {
            this.state.tipoExpedientes = await this.orm.searchRead('expediente.tipo', [], ['id', 'name']);
        } catch (error) {
            this.notification.add("No se pudo cargar el listado de tipos de expediente", { type: "danger" });
        }
    }

    async initExpedientePrincipal() {
        try {
            const regis = await this.orm.searchRead('expediente.tipo', [['expediente_principal', '=', true]], ['id', 'name']);
            if (regis.length > 0) {
                this.state.idExpediente = regis[0].id;
                await this.recomputeValidacion();
            }
        } catch (error) {
            console.error("Error al inicializar expediente principal:", error);
        }
    }

    async onChangeExpediente(ev) {
        const val = ev.target.value;
        this.state.idExpediente = val === "todos" ? null : parseInt(val) || null;
        await this.recomputeValidacion();
    }

    async onChangePlaza(ev) {
        const val = ev.target.value;
        const plazaId = val === "todos" ? null : parseInt(val);
        this.state.selectedPlaza = plazaId;

        const domain = plazaId
            ? [['flotilla_id', '=', 1], ['plaza_id', '=', plazaId]]
            : [['flotilla_id', '=', 1]];

        await this.loadVehiculos(domain);
        await this.recomputeValidacion();
    }

    async recomputeValidacion() {
        if (!this.state.idExpediente || this.state.vehiculos.length === 0) {
            this.state.VehiculosExpediente = [];
            this.state.expeIncompletos = [];
            this.state.expeCompletos = [];
            return;
        }
        try {
            console.time("🚀 recomputeValidacion TOTAL");
            const vehicleIds = this.state.vehiculos.map(v => v.id);
            console.time("📤 ORM CALL - Python/Odoo");
            const validaciones = await this.orm.call(
                'fleet.vehicle',
                'return_validacion_expe',
                [vehicleIds, this.state.idExpediente],
                {}
            );
            console.timeEnd("📤 ORM CALL - Python/Odoo");
            console.time("⚙️ Procesamiento JS");
            this.state.VehiculosExpediente = validaciones;
            console.log(this.state.VehiculosExpediente)
            this.state.expeIncompletos = validaciones.filter(
                item => item.expediente === false
            );
            console.log(this.state.expeIncompletos)
            this.state.expeCompletos = validaciones.filter(
                item => item.expediente === true
            );
            console.log(this.state.expeCompletos)
            this.state.currentPage = 1;
            console.timeEnd("⚙️ Procesamiento JS");
            console.log("📊 Estadísticas:", {
                vehiculos: vehicleIds.length,
                validaciones: validaciones.length,
                incompletos: this.state.expeIncompletos.length,
                completos: this.state.expeCompletos.length,
            });
            this.state.expeCompletosInt = this.state.expeCompletos.length
            this.state.expeIncompletosInt = this.state.expeIncompletos.length
            console.timeEnd("🚀 recomputeValidacion TOTAL");
        } catch (error) {
            console.error("Error al recomputar validaciones:", error);
            this.notification.add(
                "Error al validar expedientes",
                { type: "danger" }
            );
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

    async abrirModal(vehiculo) {
        this.state.vehiculoSeleccionado = vehiculo;
        this.state.archivosVehiculo = null;
        this.state.isLoadingArchivos = true;
        console.log(this.state.vehiculoSeleccionado)
        try {
            if (this.state.idExpediente) {
                this.state.archivosVehiculo = await this.orm.call(
                    'fleet.vehicle', 'get_expediente_type',
                    [this.state.idExpediente, vehiculo.id], {}
                );
                console.log(this.state.archivosVehiculo);
            } else {
                this.state.archivosVehiculo = await this.orm.call(
                    'fleet.vehicle', 'get_expediente', [vehiculo.id], {}
                );
            }
        } catch (error) {
            console.error("Error al cargar documentos del vehículo:", error);
            this.notification.add("No se pudieron cargar los documentos del vehículo", { type: "danger" });
        } finally {
            this.state.isLoadingArchivos = false;
        }
    }

    cerrarModal() {
        this.state.vehiculoSeleccionado = null;
        this.state.archivosVehiculo = null;
        this.closePreview();
    }


    async descargarArchivo(fileObj) {
        if (!fileObj || !fileObj.data) {
            this.notification.add("El archivo no está disponible.", { type: "warning" });
            return;
        }
        const mime = fileObj.mimetype || 'application/pdf';
        this._descargarBase64(fileObj.data, fileObj.doc_name || 'documento.pdf', mime);
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
        if (!fileObj || !fileObj.data) {
            this.notification.add("El archivo no está disponible.", { type: "warning" });
            return;
        }

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

    closePreview() {
        if (this.state.pdfUrl) {
            URL.revokeObjectURL(this.state.pdfUrl);
        }
        this.state.pdfUrl = null;
        this.state.isOpen = false;
    }


    async descargarZip() {
        if (!this.state.vehiculoSeleccionado || !this.state.vehiculoSeleccionado.id) return;
        this.state.isDownloadingZip = true;
        try {
            const zipDoc = await this.orm.call(
                'fleet.vehicle', 'get_zip_expediente',
                [this.state.vehiculoSeleccionado.id, this.state.idExpediente], {}
            );
            if (!zipDoc) {
                this.notification.add("No hay documentos disponibles para descargar.", { type: "warning" });
                return;
            }
            this._descargarBase64(zipDoc.data, zipDoc.name, zipDoc.mimetype);
        } catch (error) {
            console.error("Error al generar ZIP:", error);
            this.notification.add("No se pudo generar el ZIP del expediente", { type: "danger" });
        } finally {
            this.state.isDownloadingZip = false;
        }
    }
}

Expediente.template = 'expediente.main';
Expediente.components = {};

registry.category('actions').add('expediente', Expediente);