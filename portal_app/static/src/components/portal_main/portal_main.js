/** @odoo-module **/
import { App, Component, useState, whenReady, useRef } from "@odoo/owl";
import { getTemplate } from "@web/core/templates";
import { loadCSS } from '@web/core/assets';

const { onWillStart, onWillUnmount, onMounted } = owl;

class LoginView extends Component {
    static template = "portal_app.Login";
    static props = { ingresar: Function }; 

    setup(){
        this.userInputRef = useRef('userInput');
        this.errorModalRef = useRef('errorModal');
    }

    async ingresar() {
        const input = this.userInputRef.el;
        const valor = input ? input.value.trim() : '';
        console.log(`[LoginView] -> Iniciando proceso. Valor ingresado: "${valor}"`);
        if (valor) {
            console.log("[LoginView] -> Enviando valor al componente padre...");
            const exito = await this.props.ingresar(valor);
            console.log(`[LoginView] -> El padre respondió. ¿Éxito de búsqueda?: ${exito}`);
            if (!exito) {
                console.log("[LoginView] -> DISPARANDO MODAL: No se encontraron datos en ningún flujo.");
                $('#noDataModal').modal('show');
            }
        } else {
            console.warn("[LoginView] -> Intento de ingreso con campo vacío.");
            input?.focus();
            input?.classList.add('is-invalid');
            setTimeout(() => input?.classList.remove('is-invalid'), 2000);
        }
    }
}

class HomeView extends Component {
    static template = "portal_app.Home";
    static props = { vehiculoId: Number, llamada_fetch: Function };

    setup(){
        this.state = useState({ files: null });
        onWillStart(this.willStart);
    }

    async willStart() {
        console.log(`[HomeView] -> Inicializando vista. Buscando pólizas para Vehículo.`);
        await this.busqueda_polizas(this.props.vehiculoId, '2026-02-03');
    }

    async busqueda_polizas(vehiculo_id, fecha) {
        console.log(`[HomeView] -> Solicitando`);
        const data = await this.props.llamada_fetch("/portal/poliza-data", {
            vehiculo: vehiculo_id
        });
        
        console.log("[HomeView] -> Respuesta de /portal/poliza-data recibida");
        
        if (!data) {
            console.error("[HomeView] -> La respuesta de pólizas regresó vacía (null/undefined)");
            return;
        }
        
        const archivos = [...(data.endosos || [])];
        if (data.poliza) {
            archivos.push(data.poliza);
        }
        this.state.files = archivos;
        console.log(archivos)
        console.log(`[HomeView] -> Estado de archivos actualizado. Total: ${archivos.length} archivos.`);
    }

    async log_poliza(ev,file){
        if (file.tipo === 'Póliza'){
            await this.props.llamada_fetch("/portal/log", {
                vehiculo_id: this.props.vehiculoId
            });
        }
    }
}
class PortalAppMain extends Component {
    static template = "portal_app.PortalMain";
    static components = { LoginView, HomeView };

    setup() {
        this.state = useState({ 
            view: "login",       
            userValue: "",      
            vehiculoId: null,   
        });
        onWillStart(this.willStart);
    }

    async willStart() {
        await loadCSS('/portal_app/static/src/css/style.css');
    }

    goHome() { 
        console.log("[PortalAppMain] -> Cambiando estado de vista a: HOME");
        this.state.view = "home"; 
    }
    
    goLogin() { 
        console.log("[PortalAppMain] -> Cambiando estado de vista a: LOGIN");
        this.state.view = "login"; 
    }
        
    async llamada_fetch(ruta, params){
        console.log(`[Fetch RPC] -> Realizando POST`);
        try {
            const response = await fetch(ruta, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: params,
                    id: 1,
                }),
            });
            const data = await response.json();
            console.log(`[Fetch RPC] <- Respuesta cruda `);
            return data.result || null;
        } catch (error) {
            console.error(`[Fetch RPC] ❌ ERROR en petición `);
            return null;
        }
    }

    async redirect_home(){
        console.log(`[PortalAppMain] -> Redirección exitosa. Vehículo asignado`);
        this.state.view = 'home';
    }

    async ingresar(valor){
        let vehiculo = null;
        this.state.userValue = valor;
        
        console.log(`[PortalAppMain] -> [FLUJO 1]: Buscando por Usuario (RFC/CURP/CIE)`);
        const data = await this.llamada_fetch("/portal/user-data", {'valor': valor});
        
        if (data && data.id){
            console.log(`[PortalAppMain] -> [FLUJO 1]: Usuario encontrado. Buscando su vehículo...`);
            vehiculo = await this.llamada_fetch("/portal/vehiculo-data", {'user': data.id, 'matricula': null});
            
            if (vehiculo && vehiculo.id){
                console.log(`[PortalAppMain] -> [FLUJO 1 CRÍTICO]: Vehículo encontrado para el usuario.`);
                this.state.vehiculoId = vehiculo.id;
                await this.redirect_home();
                return true; 
            }
            console.warn(`[PortalAppMain] -> [FLUJO 1]: El usuario existe, pero /portal/vehiculo-data NO regresó ningún vehículo.`);
            return false; 
        }
        
        console.log(`[PortalAppMain] -> [FLUJO 2]: No fue usuario. Probando búsqueda por Número de Contrato...`);
        const data_contrato = await this.llamada_fetch('/portal/contrato-data', {'valor': valor });
        
        if (data_contrato && data_contrato.vehicle_id){
            console.log(`[PortalAppMain] -> [FLUJO 2 CRÍTICO]: Contrato válido hallado.`);
            this.state.vehiculoId = data_contrato.vehicle_id;
            await this.redirect_home();
            return true; 
        }
        
        console.log(`[PortalAppMain] -> [FLUJO 3]: No fue contrato. Pasando a validación directa por Placa / Matrícula...`);
        vehiculo = await this.llamada_fetch("/portal/vehiculo-data", {'user': null, 'matricula': valor});
        
        if (vehiculo && vehiculo.id){
            console.log(`[PortalAppMain] -> [FLUJO 3 CRÍTICO]: Vehículo localizado por Placa/Matrícula.`);
            this.state.vehiculoId = vehiculo.id;
            await this.redirect_home();
            return true; 
        }
        
        console.error(`[PortalAppMain] -> [FIN DEL FLUJO]: El valor "${valor}" no coincidió con Usuario, Contrato ni Placa.`);
        return false;
    }
}

whenReady(async () => {
    const rootElement = document.getElementById("portal_main");
    if (rootElement) {
        console.log("[OWL App] -> Inicializando PortalAppMain en #portal_main...");
        const app = new App(PortalAppMain, {
            getTemplate,
            dev: odoo.debug,
        });
        await app.mount(rootElement);
        console.log("[OWL App] -> Aplicación montada con éxito.");
    }
});