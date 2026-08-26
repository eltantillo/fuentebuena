document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById("formulario");
    const btn = document.getElementById("btn_submit");
    const forms = document.querySelectorAll('.needs-validation');
    const selectMedio = document.getElementById('medio');

    Array.prototype.forEach.call(forms, function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            else {
                btn.disabled = true;
                btn.innerText = "Enviando..."
            }
            form.classList.add('was-validated');
        }, false);
    });
});

