document.addEventListener('DOMContentLoaded', () => {
    const divDatos = document.getElementById('convenios-data');

    if (divDatos) {
        const convenios = JSON.parse(divDatos.dataset.convenios);
        const selectEstado = document.getElementById("estado");
        const divConvenio = document.getElementById("convenio");
        const selectConvenio = document.getElementById("convenio_select");
        selectEstado.addEventListener('change', function () {
            const valorEstado = parseInt(selectEstado.value);
            const convenios_filtrado = convenios.filter(convenio =>
                parseInt(convenio.estado) === valorEstado
            );
            selectConvenio.innerHTML = '';
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Seleccione una opción';
            selectConvenio.appendChild(defaultOption);
            if (convenios_filtrado.length > 0) {
                convenios_filtrado.forEach(opcion => {
                    const option = document.createElement('option');
                    option.value = opcion.id;
                    option.textContent = opcion.name;
                    selectConvenio.appendChild(option);
                });
                divConvenio.classList.remove("no-mostrar");
            } else {
                divConvenio.classList.add("no-mostrar");
            }
        });
    } else {

        console.error("No existe el div con id='datos'");
    }
});