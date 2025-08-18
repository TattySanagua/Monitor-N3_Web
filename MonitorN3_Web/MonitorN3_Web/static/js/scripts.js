document.addEventListener("DOMContentLoaded", function() {

    // Menú desplegable
    document.querySelectorAll('.dropdown-submenu .dropdown-toggle').forEach(function(element) {
        element.addEventListener("click", function(event) {
            event.preventDefault();
            event.stopPropagation();
            let submenu = this.nextElementSibling;
            if (submenu) {
                submenu.classList.toggle("show");
            }
            document.querySelectorAll(".dropdown-submenu .dropdown-menu").forEach(function(sub) {
                if (sub !== submenu) {
                    sub.classList.remove("show");
                }
            });
        });
    });

    // Cargar scripts específicos de cada vista
    if (document.body.id === "piezometro-page") {
        initPiezometro();
    }
    if (document.body.id === "parshall-page") {
        initParshall();
    }
    if (document.body.id === "volumetrico-page") {
        initVolumetrico();
    }
    if (document.body.id === "freatimetro-page") {
        initFreatimetro();
    }
});

// Función para Piezómetros
function initPiezometro() {
    document.getElementById("calcular-np").addEventListener("click", function() {
        const idInstrumento = document.querySelector('select[name="id_instrumento"]').value;
        const lectura = parseFloat(document.getElementById("lectura").value);

        if (!idInstrumento) {
            alert("Por favor, seleccione un piezómetro.");
            return;
        }

        fetch('/medicion/piezometro/nueva', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({ id_instrumento: idInstrumento, lectura: lectura })
        })
        .then(response => response.json())
        .then(data => {
            if (data.nivel_piezometrico) {
                document.getElementById("valor-np").textContent = data.nivel_piezometrico;
                document.getElementById("nivel_piezometrico").value = data.nivel_piezometrico;
                document.getElementById("resultado-np").style.display = "block";
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    });
}

// Función para Parshall
function initParshall() {
    document.getElementById("calcular-caudal").addEventListener("click", function() {
        const idInstrumento = document.querySelector('select[name="id_instrumento"]').value;
        const lectura_ha = parseFloat(document.getElementById("lectura_ha").value);

        if (!idInstrumento || isNaN(lectura_ha)) {
            alert("Por favor, seleccione un aforador y proporcione una lectura válida de ha.");
            return;
        }

        fetch("/medicion/afoparshall/nueva", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({ id_instrumento: idInstrumento, lectura_ha: lectura_ha })
        })
        .then(response => response.json())
        .then(data => {
            if (data.caudal) {
                document.getElementById("caudal").textContent = data.caudal.toFixed(3);
                document.getElementById("caudal_calculado").value = data.caudal.toFixed(3);
                document.getElementById("resultado-caudal").style.display = "block";
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    });
}

// Función para Volumetrico
function initVolumetrico() {
    document.getElementById('calcular-caudal').addEventListener('click', function() {
            const lecturas = [
                { volumen: parseFloat(document.querySelector('input[name="volumen_1"]').value), tiempo: parseFloat(document.querySelector('input[name="tiempo_1"]').value) },
                { volumen: parseFloat(document.querySelector('input[name="volumen_2"]').value), tiempo: parseFloat(document.querySelector('input[name="tiempo_2"]').value) },
                { volumen: parseFloat(document.querySelector('input[name="volumen_3"]').value), tiempo: parseFloat(document.querySelector('input[name="tiempo_3"]').value) }
            ];

            let caudales = [];

            // Calcular cada caudal y mostrarlo en pantalla
            lecturas.forEach((lectura, index) => {
                if (!isNaN(lectura.volumen) && !isNaN(lectura.tiempo) && lectura.tiempo > 0) {
                    const caudal = lectura.volumen / lectura.tiempo;
                    caudales.push(caudal);
                    document.getElementById(`caudal-${index + 1}`).textContent = caudal.toFixed(2);
                } else {
                    document.getElementById(`caudal-${index + 1}`).textContent = 'Sin valor';
                }
            });

            // Calcular el promedio y mostrarlo
            if (caudales.length > 0) {
                const caudalPromedio = caudales.reduce((acc, val) => acc + val, 0) / caudales.length;
                document.getElementById('caudal-promedio').textContent = caudalPromedio.toFixed(2);

                // Aquí aseguramos que el valor se envía en el formulario
                document.getElementById('q_promedio').value = caudalPromedio.toFixed(2);

                document.getElementById('resultado-caudales').style.display = 'block';
            } else {
                alert('Por favor, ingrese al menos un par válido de volumen y tiempo.');
                document.getElementById('resultado-caudales').style.display = 'none';
            }
        });
}
// Función para Freatimetro
function initFreatimetro() {
    document.getElementById('calcular-nf').addEventListener('click', function() {
            const idInstrumento = document.querySelector('select[name="id_instrumento"]').value;
            const lectura = parseFloat(document.getElementById('lectura').value);

            if (!idInstrumento) {
                alert('Por favor, seleccione un freatímetro.');
            return;
            }

            fetch('/medicion/freatimetro/nueva', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector("[name=csrfmiddlewaretoken]").value,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    'id_instrumento': idInstrumento,
                    'lectura': lectura
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.nivel_freatico) {
                    document.getElementById('valor-nf').textContent = data.nivel_freatico;
                    document.getElementById('nivel_freatico').value = data.nivel_freatico;
                    document.getElementById('resultado-nf').style.display = 'block';
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
}