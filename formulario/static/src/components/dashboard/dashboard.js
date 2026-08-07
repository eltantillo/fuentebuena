import { user } from '@web/core/user';
import { registry } from '@web/core/registry';
import { rpc } from '@web/core/network/rpc';
import { session } from '@web/session'
import { useService } from '@web/core/utils/hooks';
import { useSetupAction } from '@web/search/action_hook';
import { loadJS } from '@web/core/assets';

const {Component, useState, onWillStart, onWillUnmount, onMounted} = owl;


class DashboardFormulario extends Component{
    setup(){
        this.orm = useService('orm');
        this.action = useService('action');
        this.rpc = rpc

        this.state = useState({
            totalPSinBuro:0,
            totalPSinBuroHoy:0,
            totalBolsaTrabajo:0,
            totalBolsaTrabajoHoy:0,
            totalSolicita:0,
            totalSolicitaHoy:0,
            totalProspecto:0,
            totalProspectoHoy:0,
            totalProspectoColab:0,
            totalProspectoColabHOy:0,
            totalProspectoAnim:0,
            totalProspectoAnimHoy:0,
            totalAfiliaDep:0,
            totalAfiliaDepHoy:0,
            totalEmpresas:0,
            totalEmpresasHoy:0,
        })

        useSetupAction();
        onWillStart(this.willStart);
        onMounted(this.mounted);
        onWillUnmount(this.willUnmount);
    }

    async willStart(){
        await loadJS('/cita_mantenimiento/static/lib/chart/chart.js');
        await this.formularios_contados()
    }

    async mounted(){
        setTimeout(() =>{
        });
    }

    async formularios_contados(){
        this.state.totalPSinBuro = await this.orm.searchCount(
            'formulario.prestamo.sin.buro',
            []
        );
        this.state.totalBolsaTrabajo = await this.orm.searchCount(
            'formulario.bolsa.trabajo',
            []
        );
        this.state.totalSolicita = await this.orm.searchCount(
            'formulario.solicita',
            []
        );
        this.state.totalProspecto = await this.orm.searchCount(
            'formulario.prospecto',
            []
        );
        this.state.totalProspectoColab = await this.orm.searchCount(
            'formulario.prospecto.colaborador',
            []
        );
        this.state.totalProspectoAnim = await this.orm.searchCount(
            'formulario.prospecto.animador',
            []
        );
        this.state.totalAfiliaDep = await this.orm.searchCount(
            'formulario.dependencia',
            []
        );
        this.state.totalEmpresas = await this.orm.searchCount(
            'formulario.empresa',
            []
        );
        const hoyInicio = new Date();
        hoyInicio.setHours(0, 0, 0, 0);
        const hoyFin = new Date();
        hoyFin.setHours(23, 59, 59, 999);
        const formatoFecha = (date) => date.toISOString().replace('T', ' ').substring(0, 19);
        this.state.totalPSinBuroHoy = await this.orm.searchCount(
            'formulario.prestamo.sin.buro',
            [
                ['create_date', '>=', formatoFecha(hoyInicio)],
                ['create_date', '<=', formatoFecha(hoyFin)]
            ]
        );
        this.state.totalBolsaTrabajoHoy = await this.orm.searchCount(
            'formulario.bolsa.trabajo',
            [
                ['create_date', '>=', formatoFecha(hoyInicio)],
                ['create_date', '<=', formatoFecha(hoyFin)]
            ]
        );
        this.state.totalSolicitaHoy = await this.orm.searchCount(
            'formulario.solicita',
            [
                ['create_date', '>=', formatoFecha(hoyInicio)],
                ['create_date', '<=', formatoFecha(hoyFin)]
            ]
        );
        this.state.totalProspectoHoy = await this.orm.searchCount(
            'formulario.prospecto',
            [
                ['create_date', '>=', formatoFecha(hoyInicio)],
                ['create_date', '<=', formatoFecha(hoyFin)]
            ]
        );
        this.state.totalProspectoColabHOy = await this.orm.searchCount(
            'formulario.prospecto.colaborador',
            [
                ['create_date', '>=', formatoFecha(hoyInicio)],
                ['create_date', '<=', formatoFecha(hoyFin)]
            ]
        );

        this.state.totalProspectoAnimHoy= await this.orm.searchCount(
            'formulario.prospecto.animador',
            [
                ['create_date', '>=', formatoFecha(hoyInicio)],
                ['create_date', '<=', formatoFecha(hoyFin)]
            ]
        );
        this.state.totalAfiliaDepHoy = await this.orm.searchCount(
            'formulario.dependencia',
            [
                ['create_date', '>=', formatoFecha(hoyInicio)],
                ['create_date', '<=', formatoFecha(hoyFin)]
            ]
        );
        this.state.totalEmpresasHoy = await this.orm.searchCount(
            'formulario.empresa',
            [
                ['create_date', '>=', formatoFecha(hoyInicio)],
                ['create_date', '<=', formatoFecha(hoyFin)]
            ]
        );
        console.log("Datos de totales hoy")
        console.log("Formulario prestamo sin buro hoy: " + this.state.totalPSinBuroHoy)
        console.log("Formulario bolsa trabajo hoy: " + this.state.totalBolsaTrabajoHoy)
        console.log("Formulario Solicita hoy: " + this.state.totalSolicitaHoy)
        console.log("Formulario Prospecto hoy: " + this.state.totalProspectoHoy)
        console.log("Formulario Prospecto colaborador hoy: " + this.state.totalProspectoColabHOy)
        console.log("Formulario Prospecto animador hoy: " + this.state.totalProspectoAnimHoy)
        console.log("Formulario dependencia sin buro hoy: " + this.state.totalPSinBuroHoy)
        console.log("Formulario empresa sin buro hoy: " + this.state.totalPSinBuroHoy)
    }

    async willUnmount() {
        /**
         *
        */
    }

    return_vista_cita(dominio, type, res_model) {
        this.action.doAction({
            name: 'Fomulario /' + type,
            type: 'ir.actions.act_window',
            res_model: res_model,
            views: [
                [false,'list'],
                [false,'form'],
            ],
            view_mode : 'list',
            domain: [
                ...dominio,
            ]
        },{
            onClose: async () =>{
            }
        });
    }

    async ver_formulario(ev){
        var dominio = []
        const state = ev.currentTarget.dataset.state;
        if (state == 'Préstamo sin buro'){
            this.return_vista_cita(dominio,state,'formulario.prestamo.sin.buro');
        }
        else if (state == 'Bolsa de trabajo'){
            this.return_vista_cita(dominio,state,'formulario.bolsa.trabajo');
        }
        else if (state == 'Solicita'){
            this.return_vista_cita(dominio,state,'formulario.solicita');
        }
        else if (state == 'Prospectos'){
            
        }
        else if (state == 'Afilia tu Dependencia'){
            this.return_vista_cita(dominio,state,'formulario.dependencia');
        }
        else if (state == 'Empresas'){
            this.return_vista_cita(dominio,state,'formulario.empresa');            
        }

    }


}

DashboardFormulario.template = 'formulario.dashboard';
DashboardFormulario.components = {};

registry.category('actions').add('formulario_dashboard', DashboardFormulario);