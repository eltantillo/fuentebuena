document.addEventListener('DOMContentLoaded', () => {
    const divMunicipio = document.getElementById('municipios-data');
    const selectEstado = document.getElementById('estado');
    const selectMunicipio = document.getElementById('municipio');

    if (divMunicipio && selectEstado && selectMunicipio) {
        const municipiosData = JSON.parse(divMunicipio.dataset.convenios || '[]');
        console.log(municipiosData)

        selectEstado.addEventListener('change', function () {
            let estadoTexto = selectEstado.options[selectEstado.selectedIndex].text.trim();
            if (estadoTexto === 'Coahuila'){
                estadoTexto = 'Coahuila de Zaragoza'
            }
            else if (estadoTexto === 'Michoacán' ){
                estadoTexto = 'Michoacán de Ocampo'
            }
            else if (estadoTexto === 'Veracruz' ){
                estadoTexto = 'Veracruz de Ignacio de la Llave'
            }
            console.log(estadoTexto)

            selectMunicipio.innerHTML = '<option value="">Seleccione una opción</option>';

            if (!selectEstado.value) {
                return;
            }
            const municipiosFiltrados = municipiosData.filter(m => m.estado === estadoTexto);
            municipiosFiltrados.forEach(m => {
                const option = document.createElement('option');
                option.value = m.id;
                option.textContent = m.municipio;
                selectMunicipio.appendChild(option);
            });
        });
    }
});