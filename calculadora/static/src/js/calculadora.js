function actualizar() {
    const monto = parseInt(document.getElementById("monto").value);
    const plazo = parseInt(document.getElementById("plazo").value);

    document.getElementById("montoLabel").innerText = `$${monto.toLocaleString()}`;

    const interes = 0.54;
    const interes_total = monto * interes;
    const total_a_pagar = monto + interes_total;

    const pago = total_a_pagar / plazo;
    document.getElementById("pagoLabel").innerText = `$${pago.toFixed(2)}`;
}

function cambiarMonto(cambio) {
    const slider = document.getElementById("monto");
    let nuevo = parseInt(slider.value) + cambio;
    if (nuevo >= 5000 && nuevo <= 150000) {
        slider.value = nuevo;
        actualizar();
    }
}

actualizar();
