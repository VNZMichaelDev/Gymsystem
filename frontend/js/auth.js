// Authentication module
import { loginAPI, validateToken } from './api.js';

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Auth.js: DOM cargado.');

    // 1. VERIFICAR SI YA HAY UNA SESIÓN VÁLIDA
    const hasValidSession = await validateToken();
    if (hasValidSession) {
        console.log('Auth.js: Sesión válida encontrada. Redirigiendo al dashboard...');
        window.location.href = 'dashboard.html';
        return; // Detiene la ejecución para no mostrar el login
    }

    console.log('Auth.js: No hay sesión válida. Mostrando formulario de login.');

    // 2. CONFIGURAR EL FORMULARIO DE LOGIN (si no fuimos redirigidos)
    const loginForm = document.getElementById('loginForm');
    const loginMsg = document.getElementById('loginMsg');

    if (!loginForm) {
        console.error('Auth.js: No se encontró el formulario #loginForm.');
        return;
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const email = loginForm.querySelector('#email').value;
        const password = loginForm.querySelector('#password').value;

        // Deshabilitar botón y limpiar mensajes
        submitBtn.disabled = true;
        submitBtn.textContent = 'Iniciando...';
        loginMsg.textContent = '';
        loginMsg.className = 'message';

        const result = await loginAPI(email, password);

        if (result.success) {
            loginMsg.textContent = result.message + ' Redirigiendo...';
            loginMsg.classList.add('success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            loginMsg.textContent = result.message;
            loginMsg.classList.add('error');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Iniciar Sesión';
        }
    });
});

// clientes.js (nuevo archivo para la página de clientes)
// Importar funciones necesarias
import { logoutAPI } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
    console.log('Clientes.js: DOM cargado.');

    // 1. CONFIGURAR CERRAR SESIÓN
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', async (e) => {
            e.preventDefault();
            console.log('Clientes.js: Cerrar sesión.');

            const result = await logoutAPI();
            if (result.success) {
                window.location.href = 'index.html'; // Redirigir a la página de login
            } else {
                alert('Error al cerrar sesión: ' + result.message);
            }
        });
    } else {
        console.warn('Clientes.js: No se encontró el botón #logoutButton.');
    }

    // ... Aquí iría el resto del código específico para la página de clientes ...
});
