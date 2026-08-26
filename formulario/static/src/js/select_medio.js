document.addEventListener("DOMContentLoaded", function (){
    const selectMedio = document.getElementById('medio');

    selectMedio.addEventListener("change", function (){
        const divMedio = document.getElementById("otro");
        const medioText = selectMedio.options[selectMedio.selectedIndex].text.trim();
        const inputText = document.getElementById("motivotext");

        if (medioText === 'Otro'){
            divMedio.classList.remove('d-none');
            inputText.required = true;
        }
        else {
            divMedio.classList.add('d-none');
        }
    });
});

