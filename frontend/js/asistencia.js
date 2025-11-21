// Asistencia module
import { authFetch, setToken, getToken } from './api.js';

const token = getToken();
if (!token) { alert('Sesión no válida. Inicia sesión.'); window.location.href = 'index.html'; }

// Elementos DOM
const btnSalir = document.getElementById('btnSalir');
const formEntrada = document.getElementById('formEntrada');
const selClienteNombre = document.getElementById('selClienteNombre');
const selClienteDNI = document.getElementById('selClienteDNI');
const selNombreSearch = document.getElementById('selNombreSearch');
const selDNISearch = document.getElementById('selDNISearch');
const msg = document.getElementById('msg');

const filtroNombre = document.getElementById('filtroNombre');
const filtroFecha = document.getElementById('filtroFecha');
const soloAbiertas = document.getElementById('soloAbiertas');
const btnBuscar = document.getElementById('btnBuscar');
const btnLimpiar = document.getElementById('btnLimpiar');
const rows = document.getElementById('rows');

// Controles de paginación
const btnPrev = document.getElementById('btnPrev');
const btnNext = document.getElementById('btnNext');
const pageInfo = document.getElementById('pageInfo');

// Variables globales
let clientesCache = [];
let asistenciasCache = [];
let filteredAsistencias = [];
let currentPage = 1;
const itemsPerPage = 10;
let selectedClienteId = null;

// Event listeners
btnSalir.onclick = () => { setToken(null); window.location.href = 'index.html'; };
btnBuscar.onclick = () => { currentPage = 1; applyFilters(); };
btnLimpiar.onclick = () => { filtroNombre.value=''; filtroFecha.value=''; soloAbiertas.checked=false; currentPage = 1; applyFilters(); };
btnPrev.onclick = () => { if (currentPage > 1) { currentPage--; renderTable(); } };
btnNext.onclick = () => { const totalPages = Math.ceil(filteredAsistencias.length / itemsPerPage); if (currentPage < totalPages) { currentPage++; renderTable(); } };

// Funciones helper
function pad2(n){ return (n<10? '0':'') + n; }
function hoyStr(){ const d=new Date(); return `${d.getFullYear()}-${pad2(d.getMonth()+1)}-${pad2(d.getDate())}`; }
function horaStr(){ const d=new Date(); return `${pad2(d.getHours())}:${pad2(d.getMinutes())}`; }

// Función para cargar clientes
async function loadClientes(){
  try{
    const r = await authFetch('/clientes/?size=1000');
    const data = await r.json();
    clientesCache = Array.isArray(data) ? data : (data.data || []);
    
    populateSelectores();
  }catch(e){
    console.error('Error cargando clientes:', e);
  }
}

// Poblar selectores de cliente
function populateSelectores() {
  // Select por nombre (solo nombres)
  selClienteNombre.innerHTML = `<option value="">Buscar por nombre...</option>` +
    clientesCache.map(c => `<option value="${c.id_cliente}">
      ${c.nombre} ${c.apellido_paterno} ${c.apellido_materno}
    </option>`).join('');
  
  // Select por DNI 
  selClienteDNI.innerHTML = `<option value="">Buscar por DNI...</option>` +
    clientesCache.map(c => `<option value="${c.id_cliente}">
      ${c.numero_documento} - ${c.nombre} ${c.apellido_paterno}
    </option>`).join('');
}

// Función para configurar filtros de búsqueda en selectores
function setupSelectFilters() {
  // Filtro de búsqueda para selector de nombres (input separado)
  if (selNombreSearch) {
    selNombreSearch.addEventListener('input', function() {
      const query = (this.value || '').toLowerCase();
      const filtered = query.length > 0
        ? clientesCache.filter(c => `${c.nombre} ${c.apellido_paterno} ${c.apellido_materno}`.toLowerCase().includes(query))
        : clientesCache;

      selClienteNombre.innerHTML = `<option value="">Buscar por nombre...</option>` +
        filtered.slice(0, 20).map(c => `<option value="${c.id_cliente}">
          ${c.nombre} ${c.apellido_paterno} ${c.apellido_materno}
        </option>`).join('');
    });
  }

  // Filtro de búsqueda para selector de DNI (input separado)
  if (selDNISearch) {
    selDNISearch.addEventListener('input', function() {
      const query = (this.value || '').toLowerCase();
      const filtered = query.length > 0
        ? clientesCache.filter(c => c.numero_documento.toLowerCase().includes(query) || `${c.nombre} ${c.apellido_paterno}`.toLowerCase().includes(query))
        : clientesCache;

      selClienteDNI.innerHTML = `<option value="">Buscar por DNI...</option>` +
        filtered.slice(0, 20).map(c => `<option value="${c.id_cliente}">
          ${c.numero_documento} - ${c.nombre} ${c.apellido_paterno}
        </option>`).join('');
    });
  }

  // Event listeners para selección (mantener sincronía entre selects)
  selClienteNombre.addEventListener('change', function() {
    selectedClienteId = this.value ? Number(this.value) : null;
    if (selectedClienteId) {
      selClienteDNI.value = String(selectedClienteId);
    }
  });
  
  selClienteDNI.addEventListener('change', function() {
    selectedClienteId = this.value ? Number(this.value) : null;
    if (selectedClienteId) {
      selClienteNombre.value = String(selectedClienteId);
    }
  });
}

// Función para cargar asistencias
async function loadAsistencias(){
  try{
    const r = await authFetch('/asistencias/');
    const data = await r.json();
    asistenciasCache = Array.isArray(data) ? data : (data.data || []);
    applyFilters();
    // cargar resumen de asistencias
    await loadAsistenciasResumen();
  }catch(e){
    rows.innerHTML = `<tr><td colspan="7">Error cargando asistencias</td></tr>`;
    console.error(e);
  }
}

// Cargar y renderizar resumen de asistencias
async function loadAsistenciasResumen(){
  const host = document.getElementById('asistResumenHost');
  if(!host) return;
  host.innerHTML = '';
  try{
    const r = await authFetch('/reportes/asistencias_resumen');
    if(!r.ok) return;
    const data = await r.json();

    const cards = [];

    cards.push({
      icon: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v6"/><path d="M12 14v8"/><path d="M5 7h14"/></svg>',
      title: 'Asistencias hoy',
      value: data.asistencias_hoy ?? 0
    });

    cards.push({
      icon: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1v22"/><path d="M3 6h18"/><path d="M3 18h18"/></svg>',
      title: 'Promedio horas por visita',
      value: `${(data.promedio_horas ?? 0).toFixed(2)} h`
    });

    cards.push({
      icon: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M12 12v6"/></svg>',
      title: 'Día con más registros',
      value: data.dia_mas_registros ? `${data.dia_mas_registros.fecha} — ${data.dia_mas_registros.cantidad}` : 'N/A'
    });

    cards.push({
      icon: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 18h18"/><path d="M12 6v6"/></svg>',
      title: 'Día con menos registros',
      value: data.dia_menos_registros ? `${data.dia_menos_registros.fecha} — ${data.dia_menos_registros.cantidad}` : 'N/A'
    });

    host.innerHTML = cards.map(c=>`
      <div class="shortcut">
        <div class="icon">${c.icon}</div>
        <div class="details">
          <div class="name">${c.title}</div>
          <div class="value">${c.value}</div>
        </div>
      </div>
    `).join('');

  }catch(e){
    console.error('Error cargando resumen de asistencias', e);
  }
}

// Función para obtener datos del cliente
function getClienteData(id){
  const c = clientesCache.find(x => x.id_cliente === id);
  if(!c) return { nombre: `Cliente ${id}`, dni: 'N/A' };
  return {
    nombre: `${c.nombre} ${c.apellido_paterno} ${c.apellido_materno}`,
    dni: c.numero_documento
  };
}

// Aplicar filtros
function applyFilters(){
  let list = [...asistenciasCache];

  const q = (filtroNombre.value || '').toLowerCase();
  if (q) {
    list = list.filter(a => {
      const c = clientesCache.find(x => x.id_cliente === a.id_cliente);
      const texto = c ? `${c.nombre} ${c.apellido_paterno} ${c.apellido_materno} ${c.numero_documento}`.toLowerCase() : '';
      return texto.includes(q);
    });
  }

  const f = (filtroFecha.value || '').trim();
  if (f) list = list.filter(a => a.fecha === f);

  if (soloAbiertas.checked) list = list.filter(a => !a.hora_salida);

  // ordenar: más recientes primero
  list.sort((a,b)=>{
    const kA = `${a.fecha} ${a.hora_entrada}`;
    const kB = `${b.fecha} ${b.hora_entrada}`;
    return kA < kB ? 1 : -1;
  });

  filteredAsistencias = list;
  currentPage = 1;
  renderTable();
}

// Renderizar tabla con paginación
function renderTable(){
  const totalPages = Math.ceil(filteredAsistencias.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const pageData = filteredAsistencias.slice(startIndex, endIndex);

  rows.innerHTML = pageData.length
    ? pageData.map(a => {
        const clienteData = getClienteData(a.id_cliente);
        return `
        <tr>
          <td>${a.id_asistencia}</td>
          <td>${clienteData.nombre}</td>
          <td>${clienteData.dni}</td>
          <td>${a.fecha}</td>
          <td>${a.hora_entrada}</td>
          <td>${a.hora_salida || '—'}</td>
          <td class="actions">
            ${a.hora_salida ? '' : `<button class="btn warn" data-salida="${a.id_asistencia}">Marcar salida</button>`}
            <button class="btn danger" data-del="${a.id_asistencia}">Eliminar</button>
          </td>
        </tr>`;
      }).join('')
    : `<tr><td colspan="7" style="text-align:center; padding: 2rem;">Sin registros</td></tr>`;

  // Actualizar info de paginación
  pageInfo.textContent = `Página ${currentPage} de ${totalPages || 1} (${filteredAsistencias.length} registros)`;
  
  // Actualizar estado de botones
  btnPrev.disabled = currentPage <= 1;
  btnNext.disabled = currentPage >= totalPages;

  // Agregar event listeners a botones de acción
  addActionListeners();
}

// Agregar event listeners a botones de acción
function addActionListeners() {
  document.querySelectorAll('[data-salida]').forEach(b=>{
    b.onclick = async ()=>{
      const id = Number(b.getAttribute('data-salida'));
      const hora = horaStr();
      if (!confirm(`Confirmar salida a las ${hora}?`)) return;
      try{
        const r = await authFetch(`/asistencias/${id}`, {
          method:'PUT',
          body: JSON.stringify({ hora_salida: hora })
        });
        if (!r.ok) throw new Error('put_failed');
        await loadAsistencias();
      }catch(e){
        alert('No se pudo marcar la salida');
      }
    };
  });

  document.querySelectorAll('[data-del]').forEach(b=>{
    b.onclick = async ()=>{
      const id = Number(b.getAttribute('data-del'));
      if (!confirm('¿Eliminar este registro de asistencia?')) return;
      try{
        const r = await authFetch(`/asistencias/${id}`, { method:'DELETE' });
        if (!r.ok) throw new Error('del_failed');
        await loadAsistencias();
      }catch(e){
        alert('No se pudo eliminar');
      }
    };
  });
}

// Marcar entrada
formEntrada.addEventListener('submit', async (e)=>{
  e.preventDefault();
  msg.textContent = 'Registrando entrada...';
  
  const id_cliente = selectedClienteId || Number(selClienteNombre.value) || Number(selClienteDNI.value);
  if(!id_cliente){ 
    msg.textContent = 'Selecciona un cliente'; 
    return; 
  }

  // Evitar doble entrada abierta (solo control frontend)
  const abierta = asistenciasCache.find(a => a.id_cliente === id_cliente && !a.hora_salida && a.fecha === hoyStr());
  if (abierta && !confirm('Este cliente ya tiene una asistencia abierta hoy. ¿Crear otra de todas formas?')) {
    msg.textContent = '';
    return;
  }

  try{
    const r = await authFetch('/asistencias/', {
      method:'POST',
      body: JSON.stringify({ id_cliente })
    });
    if (!r.ok) {
      const err = await r.json().catch(()=> ({}));
      msg.textContent = err.message || 'No se pudo registrar la entrada';
      return;
    }
    
    // Limpiar formulario
    selectedClienteId = null;
    selClienteNombre.value = '';
    selClienteDNI.value = '';
    populateSelectores();
    
    msg.textContent = 'Entrada registrada ✓';
    await loadAsistencias();
    setTimeout(()=> msg.textContent = '', 1200);
  }catch(e){
    console.error(e);
    msg.textContent = 'Error de conexión';
  }
});

// Inicialización
(async function init(){
  await loadClientes();
  setupSelectFilters();
  await loadAsistencias();
})();