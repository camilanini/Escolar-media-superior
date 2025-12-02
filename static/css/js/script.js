document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    const deleteButtons = document.querySelectorAll('.btn-danger[onclick*="eliminar"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que quieres realizar esta acción?')) {
                e.preventDefault();
            }
        });
    });

    window.mostrarNotificacion = function(mensaje, tipo = 'success') {
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
        alerta.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 1050;
            max-width: 400px;
        `;
        alerta.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alerta);
        
        setTimeout(() => {
            if (alerta.parentNode) {
                const bsAlert = new bootstrap.Alert(alerta);
                bsAlert.close();
            }
        }, 5000);
    };

    cargarAjustesTema();

    console.log('Media Superior Platform loaded successfully');
});

function cargarAjustesTema() {
    const ajustes = JSON.parse(localStorage.getItem('ajustesApariencia')) || {};
    
    if (ajustes.tema) {
        aplicarTema(ajustes.tema);
    }
    
    if (ajustes.font_size) {
        aplicarTamañoFuente(ajustes.font_size);
    }
}

function aplicarTema(tema) {
    document.body.classList.remove('tema-oscuro', 'tema-claro');
    
    if (tema === 'oscuro') {
        document.body.classList.add('tema-oscuro');
    } else if (tema === 'auto') {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('tema-oscuro');
        } else {
            document.body.classList.add('tema-claro');
        }
    } else {
        document.body.classList.add('tema-claro');
    }
}

function aplicarTamañoFuente(tamaño) {
    document.documentElement.style.fontSize = 
        tamaño === 'small' ? '14px' : 
        tamaño === 'large' ? '18px' : '16px';
}

function formatFecha(fechaStr) {
    const fecha = new Date(fechaStr);
    const opciones = { 
        weekday: 'long',
        day: 'numeric', 
        month: 'long', 
        year: 'numeric' 
    };
    return fecha.toLocaleDateString('es-ES', opciones);
}

function formatHora(horaStr) {
    if (!horaStr) return '';
    const [horas, minutos] = horaStr.split(':');
    return `${horas}:${minutos}`;
}

function validarFormulario(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

function limpiarFormulario(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        form.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
    }
}

function toggleElement(elementId, mostrar = true) {
    const element = document.getElementById(elementId);
    if (element) {
        if (mostrar) {
            element.style.display = 'block';
            element.classList.add('fade-in');
        } else {
            element.classList.add('fade-out');
            setTimeout(() => {
                element.style.display = 'none';
                element.classList.remove('fade-out');
            }, 300);
        }
    }
}