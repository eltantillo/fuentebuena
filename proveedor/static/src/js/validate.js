document.addEventListener("DOMContentLoaded", (event) => {
    const input = document.getElementById("street_0");

    console.log("Se ejectura el JS")
    console.log(input)

    if(input){
        
        input.addEventListener("input", function() {
            input.classList.remove("o_field_invalid");
        });
    };
});