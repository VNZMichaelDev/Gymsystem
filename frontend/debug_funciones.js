// Script de debug para probar las funciones globales
// Ejecutar esto en la consola del navegador para verificar que las funciones estén definidas

console.log("🔍 Verificando funciones globales...");

// Verificar funciones principales
const funcionesRequeridas = [
    'editarPago',
    'eliminarPago', 
    'verComprobante',
    'loadPaymentInfo'
];

funcionesRequeridas.forEach(funcion => {
    if (typeof window[funcion] === 'function') {
        console.log(`✅ ${funcion} está definida`);
    } else {
        console.log(`❌ ${funcion} NO está definida`);
    }
});

// Verificar variables globales
const variablesRequeridas = [
    'currentPage',
    'totalPages', 
    'loadPagos',
    'selectCliente',
    'paymentInfo',
    'currentPaymentInfo',
    'msg'
];

variablesRequeridas.forEach(variable => {
    if (typeof window[variable] !== 'undefined') {
        console.log(`✅ ${variable} está definida:`, typeof window[variable]);
    } else {
        console.log(`❌ ${variable} NO está definida`);
    }
});

// Función de prueba simple
window.testEditarPago = function() {
    console.log("🧪 Probando editarPago con ID 1...");
    if (typeof editarPago === 'function') {
        editarPago(1);
    } else {
        console.error("❌ editarPago no está definida");
    }
};

console.log("💡 Ejecuta: testEditarPago() para probar la función");