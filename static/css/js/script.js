
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Media Superior Platform initialized');
    
    initTooltips();
    initSidebar();
    initNotifications();
    initFormValidations();
    initAnimations();
    initRealTimeUpdates();
    initInteractiveComponents();
    
    showWelcomeNotification();
});

/**
 * Inicializar tooltips de Bootstrap
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover'
        });
    });
    console.log('✅ Tooltips initialized:', tooltipList.length);
}

/**
 * Inicializar funcionalidades del sidebar
 */
function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    
    if (sidebar) {
        navLinks.forEach(link => {
            link.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(8px)';
            });
            
            link.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
            });
        });
        
        if (window.innerWidth < 768) {
            makeSidebarMobileFriendly();
        }
    }
}

/**
 * Adaptar sidebar para móviles
 */
function makeSidebarMobileFriendly() {
    const sidebar = document.querySelector('.sidebar');
    const navItems = document.querySelectorAll('.sidebar .nav-item');
    
    if (sidebar) {
        sidebar.style.overflowX = 'auto';
        sidebar.style.whiteSpace = 'nowrap';
        
        navItems.forEach(item => {
            item.style.display = 'inline-block';
            item.style.marginRight = '10px';
        });
    }
}

/**
 * Inicializar sistema de notificaciones
 */
function initNotifications() {
    if (!sessionStorage.getItem('welcomeShown')) {
        setTimeout(() => {
            showNotification('¡Bienvenido de nuevo!', 'success');
            sessionStorage.setItem('welcomeShown', 'true');
        }, 1000);
    }
    
    updateNotificationBadge();
}

/**
 * Inicializar validaciones de formularios
 */
function initFormValidations() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                highlightInvalidFields(form);
            } else {
                showFormSuccess(form);
            }
            
            form.classList.add('was-validated');
        });
    });
    
    initRealTimeValidation();
}

/**
 * Inicializar animaciones
 */
function initAnimations() {
    initScrollAnimations();
    
    animateProgressBars();
    
    initCounters();
    
    initHoverEffects();
}

/**
 * Inicializar actualizaciones en tiempo real
 */
function initRealTimeUpdates() {
    updateCurrentTime();
    setInterval(updateCurrentTime, 60000);
    
    updateTaskCounters();
    
    simulateRealTimeNotifications();
}

/**
 * Inicializar componentes interactivos
 */
function initInteractiveComponents() {
    initModals();
    initAccordions();
    initTabs();
    initCalendarInteractions();
}


/**
 * Mostrar notificación toast
 */
function showNotification(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className =`alert alert-${type} alert-dismissible fade show`;
    toast.style.minWidth = '300px';
    toast.style.marginBottom = '10px';
    toast.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, duration);
    
    return toast;
}

/**
 * Obtener icono para tipo de notificación
 */
function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'bell';
}

/**
 * Crear contenedor de notificaciones si no existe
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'position-fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '1060';
    document.body.appendChild(container);
    return container;
}

/**
 * Mostrar notificación de bienvenida
 */
function showWelcomeNotification() {
    const studentName = document.querySelector('.navbar .nav-link span')?.textContent || 'Estudiante';
    showNotification('¡Bienvenido de nuevo, ' + studentName + '!', 'success', 3000);
}

/**
 * Actualizar badge de notificaciones
 */
function updateNotificationBadge() {
    const badge = document.querySelector('.navbar .badge.bg-danger');
    if (badge) {
        const newCount = Math.floor(Math.random() * 2); // 0 o 1 nueva notificación
        if (newCount > 0) {
            badge.textContent = parseInt(badge.textContent) + newCount;
            badge.style.animation = 'pulse 1s infinite';
        }
    }
}


/**
 * Resaltar campos inválidos
 */
function highlightInvalidFields(form) {
    const invalidFields = form.querySelectorAll(':invalid');
    
    invalidFields.forEach(field => {
        field.classList.add('is-invalid');
        
        if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('invalid-feedback')) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = getFieldErrorMessage(field);
            field.parentNode.appendChild(errorDiv);
        }
    });
}

/**
 * Obtener mensaje de error para campo
 */
function getFieldErrorMessage(field) {
    const fieldName = field.labels?.[0]?.textContent || 'Este campo';
    
    if (field.validity.valueMissing) {
        return fieldName + ' es requerido.';
    }
    
    if (field.validity.typeMismatch) {
        if (field.type === 'email') return 'Por favor ingresa un email válido.';
        if (field.type === 'url') return 'Por favor ingresa una URL válida.';
    }
    
    if (field.validity.patternMismatch) {
        if (field.name === 'curp') return 'La CURP debe tener 18 caracteres alfanuméricos.';
        if (field.name === 'numero_control') return 'El número de control debe tener 7 dígitos.';
    }
    
    if (field.validity.tooShort) {
        return fieldName + ' debe tener al menos ' + field.minLength + ' caracteres.';
    }
    
    return 'Por favor corrige este campo.';
}

/**
 * Mostrar éxito de formulario
 */
function showFormSuccess(form) {
    const formId = form.id || 'form';
    showNotification('¡Formulario enviado correctamente!', 'success');
    
    form.style.transform = 'scale(0.98)';
    setTimeout(() => {
        form.style.transform = 'scale(1)';
    }, 300);
}

/**
 * Inicializar validación en tiempo real
 */
function initRealTimeValidation() {
    const curpInput = document.getElementById('curp');
    if (curpInput) {
        curpInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
            validateCURP(this);
        });
    }
    
    const controlInput = document.getElementById('numero_control');
    if (controlInput) {
        controlInput.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '');
            validateControlNumber(this);
        });
    }
    
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            validateEmail(this);
        });
    }
}

/**
 * Validar formato de CURP
 */
function validateCURP(input) {
    const curpRegex = /^[A-Z]{4}[0-9]{6}[A-Z]{6}[0-9A-Z]{2}$/;
    
    if (input.value.length === 18 && !curpRegex.test(input.value)) {
        input.classList.add('is-invalid');
        showNotification('El formato de la CURP no es válido', 'warning');
    } else if (input.value.length === 18) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    }
}

/**
 * Validar número de control
 */
function validateControlNumber(input) {
    if (input.value.length === 7) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    } else if (input.value.length > 0 && input.value.length !== 7) {
        input.classList.add('is-invalid');
    }
}

/**
 * Validar email
 */
function validateEmail(input) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (input.value && !emailRegex.test(input.value)) {
        input.classList.add('is-invalid');
    } else if (input.value) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    }
}


/**
 * Inicializar animaciones al hacer scroll
 */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.card, .stats-card, .materia-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

/**
 * Animar progress bars
 */
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const width = bar.style.width || bar.getAttribute('style')?.match(/width: ([^;]+)/)?.[1];
        if (width) {
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 300);
        }
    });
}

/**
 * Inicializar contadores animados
 */
function initCounters() {
    const counters = document.querySelectorAll('.stats-number, .counter');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseFloat(entry.target.textContent);
                if (!isNaN(target)) {
                    animateCounter(entry.target, target);
                }
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
}

/**
 * Animar contador numérico
 */
function animateCounter(element, target) {
    let current = 0;
    const increment = target / 50;
    const isDecimal = target % 1 !== 0;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = isDecimal ? target.toFixed(1) : target;
            clearInterval(timer);
        } else {
            element.textContent = isDecimal ? current.toFixed(1) : Math.floor(current);
        }
    }, 30);
}

/**
 * Inicializar efectos hover
 */
function initHoverEffects() {
    const hoverElements = document.querySelectorAll('.hover-lift, .card-hover');
    
    hoverElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.zIndex = '10';
            this.style.transition = 'all 0.3s ease';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.zIndex = '1';
        });
    });
}


/**
 * Inicializar modales
 */
function initModals() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const modalContent = this.querySelector('.modal-content');
            if (modalContent) {
                modalContent.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    modalContent.style.transform = 'scale(1)';
                }, 150);
            }
        });
    });
}

/**
 * Inicializar acordeones
 */
function initAccordions() {
    const accordions = document.querySelectorAll('.accordion-button');
    
    accordions.forEach(button => {
        button.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon) {
                if (this.classList.contains('collapsed')) {
                    icon.className = 'fas fa-chevron-down';
                } else {
                    icon.className = 'fas fa-chevron-up';
                }
            }
        });
    });
}

/**
 * Inicializar pestañas
 */
function initTabs() {
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabPanes.forEach(pane => {
        pane.addEventListener('show.bs.tab', function() {
            this.style.animation = 'fadeIn 0.3s ease';
        });
    });
}

/**
 * Inicializar interacciones del calendario
 */
function initCalendarInteractions() {
    const calendarDays = document.querySelectorAll('.calendar-day');
    
    calendarDays.forEach(day => {
        day.addEventListener('click', function() {
            const dayNumber = this.textContent.trim();
            const hasEvent = this.classList.contains('has-event');
            
            calendarDays.forEach(d => d.classList.remove('selected'));
            this.classList.add('selected');
            
            if (hasEvent) {
                showDayEvents(dayNumber);
            } else {
                showNotification('Día ' + dayNumber + ' seleccionado. No hay eventos programados.', 'info');
            }
        });
    });
}

/**
 * Mostrar eventos del día
 */
function showDayEvents(dayNumber) {
    const events = [
        { time: '10:00 AM', title: 'Clase de Programación', type: 'academico' },
        { time: '12:00 PM', title: 'Tutoría Grupal', type: 'tutoria' }
    ];
    
    let eventsHTML = events.map(event => `
        <div class="alert alert-${event.type === 'academico' ? 'primary' : 'success'} mb-2">
            <strong>${event.time}</strong> - ${event.title}
        </div>
    `).join('');
    
    showNotification('Eventos para el día ' + dayNumber + ':', 'info');
    
    console.log('Eventos del día ' + dayNumber + ':', events);
}


/**
 * Actualizar hora actual
 */
function updateCurrentTime() {
    const timeElements = document.querySelectorAll('.current-time, .badge.bg-light.text-success');
    
    if (timeElements.length > 0) {
        const now = new Date();
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        const formattedTime = now.toLocaleDateString('es-ES', options);
        
        timeElements.forEach(element => {
            element.textContent = formattedTime;
        });
    }
}

/**
 * Actualizar contadores de tareas
 */
function updateTaskCounters() {
    const taskCounters = document.querySelectorAll('.badge.bg-warning');
    
    setInterval(() => {
        taskCounters.forEach(counter => {
            const current = parseInt(counter.textContent);
            if (current > 0 && Math.random() > 0.8) { 
                counter.textContent = current - 1;
                if (current - 1 === 0) {
                    counter.classList.remove('bg-warning');
                    counter.classList.add('bg-success');
                    counter.innerHTML = '<i class="fas fa-check"></i>';
                }
            }
        });
    }, 30000); 
}

/**
 * Simular notificaciones en tiempo real
 */
function simulateRealTimeNotifications() {
    setInterval(() => {
        if (Math.random() > 0.7) { 
            const notifications = [
                'Nueva tarea asignada en Programación',
                'Recordatorio: Tutoría mañana a las 1:00 PM',
                'Calificaciones del parcial disponibles',
                'Nuevo material de estudio subido'
            ];
            
            const randomNotification = notifications[Math.floor(Math.random() * notifications.length)];
            showNotification(randomNotification, 'info');
            updateNotificationBadge();
        }
    }, 120000); 
}


/**
 * Formatear fecha
 */
function formatDate(date) {
    return new Date(date).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Formatear hora
 */
function formatTime(time) {
    return new Date('2000-01-01T' + time).toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Calcular días restantes
 */
function getDaysRemaining(targetDate) {
    const target = new Date(targetDate);
    const today = new Date();
    const diffTime = target - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

/**
 * Generar ID único
 */
function generateId() {
    return 'id_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Verificar si es dispositivo móvil
 */
function isMobileDevice() {
    return window.innerWidth < 768;
}

/**
 * Prevenir envío de formularios con Enter
 */
document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && event.target.tagName !== 'TEXTAREA') {
        const form = event.target.closest('form');
        if (form && !form.classList.contains('allow-enter-submit')) {
            event.preventDefault();
        }
    }
});

window.addEventListener('error', function(event) {
    console.error('Error capturado:', event.error);
    showNotification('Ocurrió un error inesperado', 'danger');
});

window.MediaSuperior = {
    showNotification,
    formatDate,
    formatTime,
    getDaysRemaining,
    generateId,
    isMobileDevice
};

console.log('🎯 Media Superior JavaScript loaded successfully');
