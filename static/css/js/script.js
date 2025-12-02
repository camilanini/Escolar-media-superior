document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Confirmación para acciones peligrosas
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que quieres realizar esta acción?')) {
                e.preventDefault();
            }
        });
    });

    // Inicializar agenda si existe en la página
    if (document.getElementById('eventosContainer')) {
        console.log('Inicializando módulo de agenda...');
        // La agenda se inicializa desde su propio script embebido
    }

    // Inicializar filtros de anuncios si existen
    if (document.querySelector('.btn-group')) {
        console.log('Módulo de anuncios cargado');
    }

    // Función global para mostrar notificaciones
    window.mostrarNotificacion = function(mensaje, tipo = 'success') {
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
        alerta.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.prepend(alerta);
        } else {
            document.body.prepend(alerta);
        }
        
        // Auto-eliminar después de 5 segundos
        setTimeout(() => {
            if (alerta.parentNode) {
                alerta.remove();
            }
        }, 5000);
    };

    // Función para confirmar asistencia (usada en tutoria.html)
    window.confirmarAsistencia = function() {
        const boton = event.target;
        boton.textContent = '✓ Asistencia Confirmada';
        boton.classList.remove('btn-primary');
        boton.classList.add('btn-success');
        boton.disabled = true;
        
        // Mostrar mensaje de confirmación
        alert('¡Asistencia confirmada para la tutoría del Viernes 20 de Octubre!');
    };

    // Función para marcar anuncios como leídos (usada en anuncios.html)
    window.marcarComoLeido = function(boton) {
        const card = boton.closest('.card');
        card.style.opacity = '0.7';
        card.style.backgroundColor = '#f8f9fa';
        boton.textContent = '✓ Leído';
        boton.classList.remove('btn-outline-primary');
        boton.classList.add('btn-outline-success');
        boton.disabled = true;
        
        // Guardar en localStorage
        const titulo = card.querySelector('.card-title').textContent.trim();
        const leidos = JSON.parse(localStorage.getItem('anunciosLeidos')) || [];
        if (!leidos.includes(titulo)) {
            leidos.push(titulo);
            localStorage.setItem('anunciosLeidos', JSON.stringify(leidos));
        }
        
        mostrarNotificacion('Anuncio marcado como leído', 'success');
    };

    // Función para filtrar anuncios (usada en anuncios.html)
    window.filtrarAnuncios = function(categoria) {
        const anuncios = document.querySelectorAll('.card.mb-3');
        const botones = document.querySelectorAll('.btn-group .btn');
        
        // Actualizar botones activos
        botones.forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');
        
        anuncios.forEach(anuncio => {
            if (categoria === 'todos') {
                anuncio.style.display = 'block';
            } else if (categoria === 'academicos') {
                // Mostrar solo anuncios académicos
                const titulo = anuncio.querySelector('.card-title').textContent;
                const esAcademico = titulo.includes('Becas') || 
                                   titulo.includes('Clases') || 
                                   titulo.includes('Horarios') ||
                                   titulo.includes('Exámenes') ||
                                   titulo.includes('Calificaciones');
                anuncio.style.display = esAcademico ? 'block' : 'none';
            } else if (categoria === 'administrativos') {
                // Mostrar solo anuncios administrativos
                const titulo = anuncio.querySelector('.card-title').textContent;
                const esAdministrativo = titulo.includes('Administrativo') || 
                                       titulo.includes('Trámites') ||
                                       titulo.includes('Documentación');
                anuncio.style.display = esAdministrativo ? 'block' : 'none';
            }
        });
    };

    // Inicializar estado de anuncios leídos al cargar la página
    if (document.querySelector('.card.mb-3')) {
        const leidos = JSON.parse(localStorage.getItem('anunciosLeidos')) || [];
        const anuncios = document.querySelectorAll('.card.mb-3');
        
        anuncios.forEach(anuncio => {
            const titulo = anuncio.querySelector('.card-title').textContent.trim();
            const boton = anuncio.querySelector('.btn-outline-primary');
            
            if (leidos.includes(titulo) && boton) {
                anuncio.style.opacity = '0.7';
                anuncio.style.backgroundColor = '#f8f9fa';
                boton.textContent = '✓ Leído';
                boton.classList.remove('btn-outline-primary');
                boton.classList.add('btn-outline-success');
                boton.disabled = true;
            }
        });
    }

    // Función para exportar datos (usada en ajustes.html)
    window.exportarDatos = function() {
        const datos = {
            perfil: JSON.parse(localStorage.getItem('alumnoData') || '{}'),
            eventos: JSON.parse(localStorage.getItem('eventosAgenda') || '[]'),
            anunciosLeidos: JSON.parse(localStorage.getItem('anunciosLeidos') || '[]'),
            fechaExportacion: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(datos, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `datos_media_superior_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        mostrarNotificacion('Datos exportados correctamente', 'success');
    };

    // Función para eliminar cuenta (usada en ajustes.html)
    window.eliminarCuenta = function() {
        if (confirm('¿Estás seguro de que quieres eliminar tu cuenta? Esta acción no se puede deshacer.')) {
            // Aquí normalmente harías una petición al servidor
            localStorage.clear();
            mostrarNotificacion('Cuenta eliminada correctamente. Redirigiendo...', 'warning');
            
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        }
    };

    console.log('Media Superior Platform loaded successfully');
});