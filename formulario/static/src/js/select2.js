document.addEventListener('DOMContentLoaded', function() {
    $('select[name="convenio_id"]').select2({
        placeholder: "Buscar convenio...",
        allowClear: true,
        width: '100%'
    });
});