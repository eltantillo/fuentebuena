import { user } from '@web/core/user';
import { registry } from '@web/core/registry';
import { rpc } from '@web/core/network/rpc';
import { session } from '@web/session'
import { useService } from '@web/core/utils/hooks';
import { useSetupAction } from '@web/search/action_hook';
import { loadJS } from '@web/core/assets';

const {Component, useState, onWillStart, onWillUnmount, onMounted} = owl;

class Dashboard extends Component {
    setup(){
        this.orm = useService('orm');
        this.action = useService('action');
        this.rpc = rpc

        this.state = useState({
            totalFacturas: 0,
            totalConfirmadas: 0,
            totalCanceladas: 0,
            totalBorrador: 0,
            totalPendientes: 0,
            totalSolicitar: 0,
            totalProveedorPendiente: 0,
            totalPorConfirmar: 0,
            usuario_factura: false,
            usuario_gerente: false,
            usuario_director: false,
            usuario: null,
            employee_id: null
        })

        useSetupAction();
        onWillStart(this.willStart);
        onMounted(this.mounted);
        onWillUnmount(this.willUnmount);
    }

    async willStart() {
        await loadJS('/factura/static/lib/chart/chart.js');
        this.state.usuario = await this.orm.read('res.users', [user.userId], ['name']);
        await this.grupo_user();
        await this.validaciones();
        await this.facturas_por_usuario();
    }

    async mounted(){
        setTimeout(() =>{
            this.renderChart();
            this.renderChart2();
        });
    }

    async validaciones(){
        if(this.state.usuario_factura === true){
            await this.orm.call('account.move' , 'validar_aprobaciones_por_solicitar', ['usuario'], {});
            await this.orm.call('account.move' , 'validar_aprobaciones_proveedor', ['usuario'], {});
        }
        else if (this.state.usuario_gerente === true){
            await this.orm.call('account.move' , 'validar_aprobaciones_por_solicitar', ['gerente_director'], {});
            await this.orm.call('account.move' , 'validar_aprobaciones_proveedor', ['gerente_director'], {});
        }
        else if(this.state.usuario_director === true){
            await this.orm.call('account.move' , 'validar_aprobaciones_por_solicitar', ['gerente_director'], {});
            await this.orm.call('account.move' , 'validar_aprobaciones_proveedor', ['gerente_director'], {});
        }
        else{
            await this.orm.call('account.move' , 'validar_aprobaciones_por_solicitar', ['all'], {});
            await this.orm.call('account.move' , 'validar_aprobaciones_proveedor', ['all'], {});
        }
    }

    async facturas_contadas(domain){
        const base_domain = domain;

        this.state.totalFacturas = await this.orm.searchCount(
            'account.move',
            [
                ...base_domain,
                ['move_type', '=', 'in_invoice'],
            ]
        );
        this.state.totalCanceladas = await this.orm.searchCount(
            'account.move',
            [
                ...base_domain,
                ['state', '=', 'cancel'],
                ['move_type', '=', 'in_invoice'],
            ]
        );
        this.state.totalConfirmadas = await this.orm.searchCount(
            'account.move',
            [
                ...base_domain,
                ['state', '=', 'posted'],
                ['move_type', '=', 'in_invoice'],
            ]
        );
        this.state.totalPendientes = await this.orm.searchCount(
            'account.move',
            [
                ...base_domain,
                ['etapa_aprobacion', '=', 'pendiente'],
                ['move_type', '=', 'in_invoice'],
            ]
        );
        this.state.totalBorrador = await this.orm.searchCount(
            'account.move',
            [
                ...base_domain,
                ['state', '=', 'draft'],
                ['move_type', '=', 'in_invoice'],
            ]
        );
        if(this.state.usuario_factura === true){
            this.state.totalSolicitar = await this.orm.searchCount(
                'account.move',
                [
                    ['create_uid','=', user.userId],
                    ['factura_para_aprobacion', '=', 'true'],
                    ['move_type', '=', 'in_invoice'],
                ]
            );
        }
        else if (this.state.usuario_gerente === true){
            this.state.totalSolicitar = await this.orm.searchCount(
                'account.move',
                [
                    ['create_uid','=', user.userId],
                    ['factura_para_aprobacion_gerente', '=', 'true'],
                    ['move_type', '=', 'in_invoice'],
                ]
            );
        }

        this.state.totalProveedorPendiente = await this.orm.searchCount(
            'account.move',
            [
                ...base_domain,
                ['proveedor_sin_confirmar', '=','true'],
                ['move_type', '=', 'in_invoice'],
            ]
        );
        this.state.totalPorConfirmar = await this.orm.searchCount(
            'account.move',
            [
                ...base_domain,
                ['factura_para_confirmar','=','true'],
                ['move_type','=','in_invoice']
            ]
        )
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

    async grupo_user(){
        this.state.usuario_factura = await this.tipo_user('factura.group_accountant_usuario_factura');
        this.state.usuario_gerente = await this.tipo_user('factura.group_accountant_gerente');
        this.state.usuario_director = await this.tipo_user('factura.group_accountant_director');
    }

    async facturas_por_usuario(){
        var dominio = [];
        var result = null;
        if(this.state.usuario_factura === true){
            dominio = [
                ['create_uid', '=', user.userId],
            ];
            await this.facturas_contadas(dominio);
        }
        else if (this.state.usuario_gerente === true || this.state.usuario_director === true){
            result = await this.orm.read('res.users', [user.userId], ['employee_id']);
            this.state.employee_id = result[0].employee_id?.[0];
            dominio = [
                '|',
                ['create_uid', '=', user.userId],
                ['create_uid.employee_id', 'child_of', this.state.employee_id]
            ];
            await this.facturas_contadas(dominio);
        }
        else{
            dominio = [];
            await this.facturas_contadas(dominio);
        }
    }

    async willUnmount() {
        /**
         *
        */
    }

    renderChart(){
        const canvas = document.getElementById('facturaChart');

        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        const ctx = canvas.getContext('2d');
        const data = {
            labels: ['Confirmadas','Borrador','Canceladas'],
            datasets: [{
                data: [this.state.totalConfirmadas, this.state.totalBorrador, this.state.totalCanceladas],
                backgroundColor: ['#28a745','#f39c12','#dc3545'],
                hoverBackgroundColor: ['#28a745', '#f39c12', '#dc3545']
            }]
        };

        new Chart(ctx, {
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
            }
        });
    }

    renderChart2(){
        const canvas = document.getElementById('facturaChart2');

        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        const ctx = canvas.getContext('2d');

        const data  = {
            labels: ['Pendientes de aprobación','Para solicitar aprobación','Pendientes de aprobación proveedor'],
            datasets: [{
                data: [this.state.totalPendientes, this.state.totalSolicitar, this.state.totalProveedorPendiente],
                backgroundColor: ['#F1C40F','#5DADE2','#A569BD'],
                hoverBackgroundColor: ['#F1C40F', '#5DADE2','#A569BD']
            }]

        };

        new Chart(ctx, {
            type: 'pie',
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
            }
        });
    }

    return_vista_factura(dominio) {
        this.action.doAction({
            name: 'Facturas',
            type: 'ir.actions.act_window',
            res_model: 'account.move',
            views: [
                [false,'list'],
                [false,'form'],
            ],
            view_mode : 'list',
            domain: [
                ...dominio,
                ['move_type', '=', 'in_invoice'],
            ]
        },{
            onClose: async () =>{

            }
        });
    }

    ver_facturas_especiales(ev){
        const tipo = `pendiente_${ev.currentTarget.dataset.tipo}`;
        var dominio = []
        if(tipo === 'pendiente_aprobacion'){
            if(this.state.usuario_factura === true){
                dominio = [
                    ['create_uid', '=', user.userId],
                    ['etapa_aprobacion', '=', 'pendiente'],
                ];
                this.return_vista_factura(dominio);
            }
            else{
                dominio = [
                    ['etapa_aprobacion', '=', 'pendiente']
                ];
                this.return_vista_factura(dominio);
            }
        }
        else if (tipo === 'pendiente_solicitar'){
            if(this.state.usuario_factura === true){
                dominio = [
                    ['create_uid', '=', user.userId],
                    ['factura_para_aprobacion', '=', 'true'],
                ];
                this.return_vista_factura(dominio);
            }
            else{
                dominio = [
                    ['factura_para_aprobacion_gerente', '=', 'true'],
                ];
                this.return_vista_factura(dominio);
            }
        }
        else if (tipo === 'pendiente_proveedor'){
            if(this.state.usuario_factura === true){
                dominio = [
                    ['create_uid', '=', user.userId],
                    ['proveedor_sin_confirmar', '=', 'true'],
                ];
                this.return_vista_factura(dominio);
            }
            else{
                dominio = [
                    ['proveedor_sin_confirmar', '=', 'true'],
                ];
                this.return_vista_factura(dominio);
            }
        }
        else if (tipo === 'pendiente_confirmar'){
            if(this.state.usuario_factura === true){
                dominio = [
                    ['create_uid', '=', user.userId],
                    ['factura_para_confirmar', '=', 'true'],
                ];
                this.return_vista_factura(dominio);
            }
            else{
                dominio = [
                    ['factura_para_confirmar', '=', 'true'],
                ];
                this.return_vista_factura(dominio);
            }
        }
    }

    ver_factura(ev){
        const state = ev.currentTarget.dataset.state;
        var dominio = [];
        if (state != 'all'){
            if (this.state.usuario_factura === true){
                dominio = [
                    ['create_uid', '=', user.userId],
                    ['state', '=', state],
                ];
                this.return_vista_factura(dominio);
            }
            else if (this.state.usuario_gerente === true ){
                dominio = [
                    ['state', '=', state],
                    '|',
                    ['create_uid', '=', user.userId],
                    ['create_uid.employee_id', 'child_of', this.state.employee_id]];
                    this.return_vista_factura(dominio)
            }
            else if (this.state.usuario_director === true){
                dominio = [
                    ['state', '=', state],
                    '|',
                    ['create_uid', '=', user.userId],
                    ['create_uid.employee_id', 'child_of', this.state.employee_id]];
                    this.return_vista_factura(dominio)
            }
            else{
                dominio = [
                    ['state', '=', state],
                ];
                this.return_vista_factura(dominio)
            }
        }
        else {
            if (this.state.usuario_factura === true){
                dominio = [
                    ['create_uid', '=', user.userId],
                ];
                this.return_vista_factura(dominio);
            }
            else{
                dominio = [];
                this.return_vista_factura(dominio)
            }
        }

    }
}

Dashboard.template = 'factura.dashboard';
Dashboard.components = {};

registry.category('actions').add('factura_dashboard', Dashboard);
