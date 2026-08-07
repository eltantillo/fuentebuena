import { user } from '@web/core/user';
import { registry } from '@web/core/registry';
import { rpc } from '@web/core/network/rpc';
import { session } from '@web/session'
import { useService } from '@web/core/utils/hooks';
import { useSetupAction } from '@web/search/action_hook';
import { loadJS } from '@web/core/assets';

const {Component, useState, onWillStart, onWillUnmount, onMounted} = owl;

class DashboardTableau extends Component {
    setup(){
        this.orm = useService('orm');
        this.action = useService('action');
        this.rpc = rpc

        this.state = useState({
            token: "",
            user_plaza: [],
            plaza: ""
        })

        useSetupAction();
        onWillStart(this.willStart);
        onMounted(this.mounted);
        onWillUnmount(this.willUnmount);
    }

    async willStart() {
        let plazas_read = await this.orm.read('res.users', [user.userId], ['plaza_ids']);
        this.state.user_plaza = plazas_read[0].plaza_ids;
        await this.asignar_plaza()
        await this.plazas()
        await this.load_token()
    }

    async plazas() {
        const plazas = await this.orm.searchRead('fleet.customer.plaza',[], ['id','name'])
        return plazas
    }

    async asignar_plaza() {
        console.log("user_plaza:", this.state.user_plaza);

        let plazas = this.state.user_plaza || [];

        if (!Array.isArray(plazas)) {
            console.error("NO es array:", plazas);
            return;
        }

        const mapaPlazas = {
            1: "PUEBLA",
            2: "MONTERREY",
            3: "QUERETARO",
            4: "LEON",
            5: "GUADALAJARA",
        };

        if (plazas.length === 0) {
            console.log("No hay plazas");
            this.state.plaza = "";
            return;
        }

        // 🔥 Convierte todos los IDs a nombres
        const nombres = plazas
            .map(id => mapaPlazas[id])
            .filter(Boolean); // elimina undefined si llega algo raro

        // 🔥 Une con coma
        this.state.plaza = nombres.join(",");

        console.log("Resultado:", this.state.plaza);
    }

    async mounted(){

    }

    async load_token(){
        const result = await rpc('/consul-token')
        this.state.token = result.token
    }

    async calular_plaza(){

    }

    async willUnmount() {
        /**
         *
        */
    }
}

DashboardTableau.template = 'dashboard_tableau.dashboard_tableau_mante';
DashboardTableau.components = {};

registry.category('actions').add('dashboard_tableau_mante', DashboardTableau);
