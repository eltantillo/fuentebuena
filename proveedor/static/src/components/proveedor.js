/** @odoo-module **/
import { registry } from '@web/core/registry';
import { useServices } from '@web/core/utils/hooks'



registry.category("actions").add("validar_js", async (env, action) => {
    const controller = env.services.action.currentController;
    if (!controller){
        console.warn("No hay controlador activo");
        return Promise.resolve();
    }
    console.log(controller)

    const orm = env.services.orm;
    const notification = env.services.notification;
    const resModel = controller.props.resModel;
    const resId = controller.currentState.resId;

    const campos = new Map();
    campos.set("name_1","complete_name");
    campos.set("vat_0","vat");
    campos.set("email_0","email");
    campos.set("street_0","street");
    campos.set("city_0","city");
    campos.set("state_id_0","state_id");
    campos.set("phone_0","phone");

    const num_campos = campos.size;
    var campos_num = 0;
    var proveedor = await orm.read(resModel,[resId],[]);
    proveedor = proveedor[0];
    var fields = ["name_1","vat_0","email_0","street_0","city_0","state_id_0","phone_0"];

    for(const [clave, valor] of campos){
        if (proveedor[`${valor}`] === false){
            const input = document.getElementById(clave);
            input.classList.add("o_field_invalid");
            //setTimeout(() =>{
            //    input.classList.remove("o_field_invalid");
            //}, 3000);
        }
        else if (proveedor[`${valor}`] != false){
            campos_num = campos_num + 1;
            const input = document.getElementById(clave);
            input.classList.remove("o_field_invalid");
        }
    }
    if (campos_num === num_campos){
        for(const field of fields){
            const input = document.getElementById(field);
            input.classList.remove("o_field_invalid");
        };
        await orm.call(resModel,'action_confirmar', [resId] ,{});
        console.log(resId)
        await env.services.action.doAction({
            type:"ir.actions.client",
            tag: "reload",
        });
        return Promise.resolve();
    }
    else{
        notification.add("Algunos campos son necesarios para confirmar el proveedor", {type: "danger", title:"Error"});
        return Promise.resolve();
    }
});
