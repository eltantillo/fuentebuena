const { registry } = require('@web/core/registry');
const bus = require('bus.BusService');
const { Component } = require('owl');
const { loadJS, loadCSS } = require('@web/core/assets')

class Notificar extends Component{
    setup(){
        loadJS('/factura/static/lib/SweetAlert/sweetalert2.js');
        loadCSS('/factura/static/lib/SweetAlert/sweetalert2.css');

        bus.addChannel("res.users");

        bus.on('notification_received',this,this._onNotification);

    }

    _onNotification(channel, notification){
        if (channel === 'simple_notification'){
            Swal.fire({
                icon:'success',
                title: notification.title,
                text: notification.message,
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 300
            })
        }
    }

}
registry.category('main_components').add('Notificar', Notificar)
