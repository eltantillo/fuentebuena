import { user } from '@web/core/user';
import { registry } from '@web/core/registry';
import { rpc } from '@web/core/network/rpc';
import { session } from '@web/session'
import { useService } from '@web/core/utils/hooks';
import { useSetupAction } from '@web/search/action_hook';
import { loadJS } from '@web/core/assets';

const {Component, useState, onWillStart, onWillUnmount, onMounted} = owl;

class DashboardCita extends Component {
    setup(){
        this.orm = useService('orm');
        this.action = useService('action');
        this.rpc = rpc

        this.state = useState({
            totalCitas: 0,
            totalProgramadas: 0,
            totalReagendadas: 0,
            totalCanceladas: 0,
            totalAsistidas: 0,
            totalInasistencia: 0,
            totalHoy: 0,
            totalTomorrow: 0,
        })

        useSetupAction();
        onWillStart(this.willStart);
        onMounted(this.mounted);
        onWillUnmount(this.willUnmount);
    }

    async willStart() {
        await loadJS('/cita_mantenimiento/static/lib/chart/chart.js');
        this.state.usuario = await this.orm.read('res.users', [user.userId], ['name']);
        await this.citas_contadas();
    }

    async mounted(){
        setTimeout(() =>{
            this.renderChart();
        });
    }


    async citas_contadas(){
        const etapas = await this.orm.searchRead(
            'cita.mantenimiento.etapa',
            [['name','in',['Programada','Reagendada','Asistida','Cancelada','Inasistencia']]],
            ['id','name']
        )
        console.log(etapas)
        const etapaMap = {};
        etapas.forEach(etapa => {
            etapaMap[etapa.name] = etapa.id
        })
        console.log(etapaMap)
        // citas programadas
        this.state.totalProgramadas = await this.orm.searchCount(
            'cita.mantenimiento',
            [['etapa_id','=', etapaMap['Programada']]]
        );
        // citas reagendadas
        this.state.totalReagendadas = await this.orm.searchCount(
            'cita.mantenimiento',
            [['etapa_id','=', etapaMap['Reagendada']]]
        );
        // citas canceladas
        this.state.totalCanceladas = await this.orm.searchCount(
            'cita.mantenimiento',
            [['etapa_id','=', etapaMap['Cancelada']]]
        );
        // citas asistidas
        this.state.totalAsistidas = await this.orm.searchCount(
            'cita.mantenimiento',
            [['etapa_id','=', etapaMap['Asistida']]]
        );
        //citas inasistidas 
        this.state.totalInasistencia = await this.orm.searchCount(
            'cita.mantenimiento',
            [['etapa_id','=', etapaMap['Inasistencia']]]
        );
        //Dates
        const hoyInicio = new Date();
        hoyInicio.setHours(0, 0, 0, 0);
        const hoyFin = new Date();
        hoyFin.setHours(23, 59, 59, 999);
        const mananaInicio = new Date();
        mananaInicio.setDate(mananaInicio.getDate() + 1);
        mananaInicio.setHours(0, 0, 0, 0);
        const mananaFin = new Date();
        mananaFin.setDate(mananaFin.getDate() + 1);
        mananaFin.setHours(23, 59, 59, 999);
        const formatoFecha = (date) => date.toISOString().replace('T', ' ').substring(0, 19);

        // --- Citas hoy ---
        this.state.totalHoy = await this.orm.searchCount(
            'cita.mantenimiento',
            [
                ['fecha_cita_inicio', '>=', formatoFecha(hoyInicio)],
                ['fecha_cita_inicio', '<=', formatoFecha(hoyFin)],
                ['etapa_id','in', [etapaMap['Programada'],etapaMap['Reagendada']]]
            ]
        );
        
        // --- Citas mañana ---
        this.state.totalTomorrow = await this.orm.searchCount(
            'cita.mantenimiento',
            [
                ['fecha_cita_inicio', '>=', formatoFecha(mananaInicio)],
                ['fecha_cita_inicio', '<=', formatoFecha(mananaFin)],
                ['etapa_id','in', [etapaMap['Programada'],etapaMap['Reagendada']]]
            ]
        );
        this.state.totalCitas = await this.orm.searchCount(
            'cita.mantenimiento',
            []
        );
    }

    async tipo_user(grupo){
        const hasgroup = await this.rpc('/web/dataset/call_kw',{
            model: 'res.users',
            method: 'has_group',
            args: [user.userId, grupo],
            kwargs: {},
        });
        return hasgroup
    } 

    async willUnmount() {
        /**
         *
        */
    }

    renderChart(){
        const canvas = document.getElementById('facturaChart');
        if (!canvas) return; 
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }
        const ctx = canvas.getContext('2d');
    
        const totalCitas =  this.state.totalCitas;
        const data = {
            labels: ['Programadas', 'Reagendadas', 'Canceladas', 'Asistidas','Inasistencia'],
            datasets: [{
                data: [this.state.totalProgramadas, this.state.totalReagendadas, this.state.totalCanceladas, this.state.totalAsistidas, this.state.totalInasistencia],
                backgroundColor: ['#f39c12', '#3498db', '#DC3545', '#28a745', '#4B5563'],
                hoverBackgroundColor: ['#f39c12', '#3498db', '#DC3545', '#28a745', '#4B5563']
            }]
        };
        this.chartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            },
            plugins: [{
                id: 'centerText',
                afterDraw: (chart) => {
                    const { ctx, chartArea: { top, bottom, left, right, width, height } } = chart;
                    ctx.save();
                    ctx.font = 'bold 24px sans-serif';
                    ctx.fillStyle = '#2c3e50'; 
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    const centerX = left + (width / 2);
                    const centerY = top + (height / 2);
                    ctx.fillText(totalCitas, centerX, centerY - 8);
                    ctx.font = '12px sans-serif';
                    ctx.fillStyle = '#7f8c8d'; 
                    ctx.fillText('Total', centerX, centerY + 14);
                    
                    ctx.restore();
                }
            }]
        });
    }

    return_vista_cita(dominio, type) {
        this.action.doAction({
            name: 'Citas /' + type,
            type: 'ir.actions.act_window',
            res_model: 'cita.mantenimiento',
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

    async ver_cita(ev){
        var dominio = [];
        const state = ev.currentTarget.dataset.state;
        if (state != 'all'){
            const formatoFecha = (date) => date.toISOString().replace('T', ' ').substring(0, 19);
            if(state == 'hoy'){
                const hoyInicio = new Date();
                hoyInicio.setHours(0, 0, 0, 0);
                const hoyFin = new Date();
                hoyFin.setHours(23, 59, 59, 999)
                const etapas = await this.orm.searchRead(
                    'cita.mantenimiento.etapa',
                    [['name','in',['Programada','Reagendada']]],
                    ['id']
                )
                dominio = [['fecha_cita_inicio', '>=', formatoFecha(hoyInicio)],
                           ['fecha_cita_inicio', '<=', formatoFecha(hoyFin)],
                           ['etapa_id', 'in', [etapas[0]['id'],etapas[1]['id']]]]
                this.return_vista_cita(dominio, state)
            }
            else if(state == 'tomorrow'){
                const mananaInicio = new Date();
                mananaInicio.setDate(mananaInicio.getDate() + 1);
                mananaInicio.setHours(0, 0, 0, 0);
                const mananaFin = new Date();
                mananaFin.setDate(mananaFin.getDate() + 1);
                mananaFin.setHours(23, 59, 59, 999);
                const etapas = await this.orm.searchRead(
                    'cita.mantenimiento.etapa',
                    [['name','in',['Programada','Reagendada']]],
                    ['id']
                )
                dominio = [['fecha_cita_inicio', '>=', formatoFecha(mananaInicio)],
                           ['fecha_cita_inicio', '<=', formatoFecha(mananaFin)],
                           ['etapa_id', 'in', [etapas[0]['id'],etapas[1]['id']]]]
                this.return_vista_cita(dominio, 'Mañana')
            }
            else {
                const etapa = await this.orm.searchRead(
                    'cita.mantenimiento.etapa',
                    [['name','=',state]],
                    ['id']
                )
                dominio = [['etapa_id','=', etapa[0]['id']]]
                this.return_vista_cita(dominio, state)
            }
        }
        else{
            dominio = [];
            this.return_vista_cita(dominio, 'Totales')
        }
    }
}

DashboardCita.template = 'cita_mantenimiento.dashboard';
DashboardCita.components = {};

registry.category('actions').add('cita_mantenimiento_dashboard', DashboardCita);
