// Detectar automáticamente la URL base según el entorno
const API_BASE_URL = window.location.origin + '/api';

/**
 * Guarda el token y los datos del usuario en el almacenamiento local.
 * @param {string} token - El token JWT.
 * @param {object} user - La información del usuario.
 */
function saveSession(token, user) {
    if (token) localStorage.setItem('token', token);
    if (user !== undefined) localStorage.setItem('user', JSON.stringify(user));
    console.log('API: Sesión guardada.');
}

export function setToken(token) {
    if (!token) {
        localStorage.removeItem('token');
        return;
    }
    localStorage.setItem('token', token);
}

/**
 * Limpia la sesión del almacenamiento local.
 */
export function clearSession() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    console.log('API: Sesión eliminada.');
}

/**
 * Obtiene el token de la sesión actual.
 * @returns {string|null}
 */
export function getToken() {
    return localStorage.getItem('token');
}

/**
 * Realiza una petición autenticada adjuntando el token JWT en la cabecera Authorization.
 * @param {string} endpoint - Ruta relativa, por ejemplo '/clientes/'.
 * @param {RequestInit} [options]
 * @returns {Promise<Response>}
 */
export async function authFetch(endpoint, options = {}) {
    const token = getToken();
    const headers = new Headers(options.headers || {});
    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }
    // No fuerces Content-Type si el body es FormData; deja que el navegador ponga el boundary
    const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;
    if (!isFormData && !headers.has('Content-Type') && options.body) {
        headers.set('Content-Type', 'application/json');
    }

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (res.status === 401 || res.status === 422) {
        // Token inválido o expirado
        clearSession();
        // Lanza un error específico que el caller puede manejar
        const msg = (await safeJson(res))?.message || 'UNAUTHORIZED';
        throw new Error(msg);
    }
    return res;
}

async function safeJson(res) {
    try { return await res.json(); } catch { return null; }
}

/**
 * Inicia sesión llamando al backend.
 * @param {string} email 
 * @param {string} password 
 * @returns {Promise<object>} - Un objeto con { success: boolean, message: string }
 */
export async function loginAPI(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Credenciales inválidas');
        }

        // Guardar token y, si el backend no envía el usuario, obtenerlo desde /auth/profile
        const token = data.access_token;
        saveSession(token, data.user);

        if (!data.user && token) {
            try {
                const profileRes = await fetch(`${API_BASE_URL}/auth/profile`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (profileRes.ok) {
                    const profileData = await profileRes.json();
                    if (profileData && profileData.user) {
                        saveSession(token, profileData.user);
                    } else {
                        // Algunos endpoints devuelven directamente el usuario
                        saveSession(token, profileData);
                    }
                }
            } catch (e) {
                console.warn('No se pudo obtener el perfil tras el login:', e);
            }
        }

        return { success: true, message: 'Inicio de sesión exitoso' };

    } catch (error) {
        console.error('API Error en login:', error);
        clearSession();
        return { success: false, message: error.message };
    }
}

/**
 * Cierra la sesión y redirige al login.
 */
export function logoutAPI() {
    clearSession();
    window.location.href = 'index.html';
}

/**
 * Valida el token actual contra el backend.
 * @returns {Promise<boolean>} - True si el token es válido, false en caso contrario.
 */
export async function validateToken() {
    const token = getToken();
    if (!token) return false;

    try {
        // En backend, la ruta disponible es GET /api/auth/profile
        const response = await fetch(`${API_BASE_URL}/auth/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
            clearSession(); // Limpia la sesión si el token es rechazado
            return false;
        }
        // Guardar/actualizar usuario si viene en la respuesta
        const data = await safeJson(response);
        if (data) {
            // Algunos endpoints guardan bajo { user: {...} }
            const user = data.user ?? data;
            if (user && typeof user === 'object') {
                saveSession(token, user);
            }
        }
        return true;
    } catch (error) {
        console.error('API Error validando token:', error);
        clearSession();
        return false;
    }
}
