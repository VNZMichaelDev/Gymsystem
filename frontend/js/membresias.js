// Membresias module
import { authFetch, setToken, getToken } from './api.js';

const token = getToken();
if (!token) { alert('Sesión no válida. Inicia sesión.'); window.location.href = 'index.html'; }

const btnSalir   = document.getElementById('btnSalir');
const form       = document.getElementById('formMemb');
const inpNombre  = document.getElementById('nombre');
const inpDur     = document.getElementById('duracion');
const inpPrecio  = document.getElementById('precio');
const btnSubmit  = document.getElementById('btnSubmit');
const btnCancel  = document.getElementById('btnCancel');
const formTitle  = document.getElementById('formTitle');
const msg        = document.getElementById('msg');

const filtro     = document.getElementById('filtro');
const btnBuscar  = document.getElementById('btnBuscar');
const btnLimpiar = document.getElementById('btnLimpiar');
const rows       = document.getElementById('rows');

btnSalir.onclick = () => { setToken(null); window.location.href = 'index.html'; };

let editingId = null;
let cache = [];

btnBuscar.onclick  = () => render();
btnLimpiar.onclick = () => { filtro.value = ''; render(); };

function toNumber(v){ const n = Number(v); return Number.isFinite(n) ? n : 0; }

function setCreateMode(){
  editingId = null;
  formTitle.textContent = 'Nueva membresía';
  btnSubmit.textContent = 'Crear';
  btnCancel.style.display = 'none';
  form.reset();
}

function setEditMode(m){
  editingId = m.id_membresia;
  formTitle.textContent = `Editar membresía #${m.id_membresia}`;
  btnSubmit.textContent = 'Guardar';
  btnCancel.style.display = 'inline-block';
  inpNombre.value = m.nombre;
  inpDur.value = m.duracion_dias;
  inpPrecio.value = m.precio;
}

btnCancel.onclick = setCreateMode;

async function load(){
  rows.innerHTML = `<tr><td colspan="5">Cargando...</td></tr>`;
  try{
    const r = await authFetch('/membresias/');
    const data = await r.json();
    cache = Array.isArray(data) ? data : (data.data || []);
    render();
      // Cargar resumen después de obtener la lista
      await loadMembresiasResumen();
  }catch(e){
    rows.innerHTML = `<tr><td colspan="5">Error cargando</td></tr>`;
    console.error(e);
  }
}

  async function loadMembresiasResumen(){
    const host = document.getElementById('membResumenHost');
    if(!host) return;
    host.innerHTML = '';
    try{
      const r = await authFetch('/reportes/membresias_resumen');
      if(!r.ok) return;
      const data = await r.json();

      const cards = [];

      // Total
      cards.push({
        icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v18H3z"/></svg>',
        title: 'Total de membresías',
        value: data.total ?? 0
      });

      // Más cara
      if(data.mas_cara){
        cards.push({
          icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3 7h7l-5.5 4 2 7L12 16l-6.5 6 2-7L2 9h7z"/></svg>',
          title: 'Membresía más cara',
          value: `${data.mas_cara.nombre} — S/ ${Number(data.mas_cara.precio).toFixed(2)}`
        });
      } else {
        cards.push({ icon:'', title:'Membresía más cara', value:'N/A' });
      }

      // Más barata
      if(data.mas_barata){
        cards.push({
          icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>',
          title: 'Membresía más barata',
          value: `${data.mas_barata.nombre} — S/ ${Number(data.mas_barata.precio).toFixed(2)}`
        });
      } else {
        cards.push({ icon:'', title:'Membresía más barata', value:'N/A' });
      }

      // Con más clientes
      if(data.con_mas_clientes){
        cards.push({
          icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>',
          title: 'Con más clientes',
          value: `${data.con_mas_clientes.nombre} — ${data.con_mas_clientes.clientes} clientes`
        });
      } else {
        cards.push({ icon:'', title:'Con más clientes', value:'N/A' });
      }

      // Con menos clientes
      if(data.con_menos_clientes){
        cards.push({
          icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 7h10v10H7z"/></svg>',
          title: 'Con menos clientes',
          value: `${data.con_menos_clientes.nombre} — ${data.con_menos_clientes.clientes} clientes`
        });
      } else {
        cards.push({ icon:'', title:'Con menos clientes', value:'N/A' });
      }

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
      console.error('Error cargando resumen de membresías', e);
    }
  }
function render(){
  const q = (filtro.value || '').toLowerCase();
  const list = q ? cache.filter(m => (m.nombre || '').toLowerCase().includes(q)) : cache;

  rows.innerHTML = list.length
    ? list.map(m => `
      <tr>
        <td>${m.id_membresia}</td>
        <td>${m.nombre}</td>
        <td>${m.duracion_dias}</td>
        <td>S/ ${Number(m.precio).toFixed(2)}</td>
        <td class="actions">
          <button class="btn warn"   data-edit="${m.id_membresia}">Editar</button>
          <button class="btn danger" data-del="${m.id_membresia}">Eliminar</button>
        </td>
      </tr>`).join('')
    : `<tr><td colspan="5">Sin resultados</td></tr>`;

  // bindings
  document.querySelectorAll('[data-edit]').forEach(b=>{
    b.onclick = () => {
      const id = Number(b.getAttribute('data-edit'));
      const m = cache.find(x => x.id_membresia === id);
      if (m) setEditMode(m);
    };
  });

  document.querySelectorAll('[data-del]').forEach(b=>{
    b.onclick = async () => {
      const id = Number(b.getAttribute('data-del'));
      if (!confirm('¿Eliminar esta membresía?')) return;
      try{
        const r = await authFetch(`/membresias/${id}`, { method:'DELETE' });
        if (!r.ok) {
          // Posible FK con clientes
          const err = await r.json().catch(()=>({}));
          alert(err.message || 'No se pudo eliminar (puede estar asignada a clientes).');
          return;
        }
        await load();
      }catch(e){
        alert('Error eliminando');
      }
    };
  });
}

form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  msg.textContent = 'Guardando...';

  const nombre = inpNombre.value.trim();
  const dur = toNumber(inpDur.value);
  const precio = toNumber(inpPrecio.value);

  if(!nombre){ msg.textContent = 'Nombre requerido'; return; }
  if(!(dur > 0)){ msg.textContent = 'Duración inválida'; return; }
  if(!(precio >= 0)){ msg.textContent = 'Precio inválido'; return; }

  try{
    let r;
    if (editingId) {
      r = await authFetch(`/membresias/${editingId}`, {
        method:'PUT',
        body: JSON.stringify({ nombre, duracion_dias: dur, precio })
      });
    } else {
      r = await authFetch('/membresias/', {
        method:'POST',
        body: JSON.stringify({ nombre, duracion_dias: dur, precio })
      });
    }
    if (!r.ok) {
      const err = await r.json().catch(()=>({}));
      msg.textContent = err.message || 'No se pudo guardar';
      return;
    }
    setCreateMode();
    msg.textContent = 'Guardado ✓';
    await load();
    setTimeout(()=> msg.textContent = '', 1200);
  }catch(e){
    console.error(e);
    msg.textContent = 'Error de conexión';
  }
});

setCreateMode();
load();
