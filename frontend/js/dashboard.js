import { authFetch, getToken, validateToken, logoutAPI, setToken } from './api.js';

function safeJson(res){ try { return res.json(); } catch { return null; } }
function formatSoles(n){ return `S/ ${Number(n||0).toFixed(2)}` }
function formatNumber(n){ return Number(n||0).toLocaleString(); }

async function loadDashboardKPIs(){
  const elIngresos = document.getElementById('kpiIngresos');
  const elClientes = document.getElementById('kpiClientes');
  const elAsistencias = document.getElementById('kpiAsistencias');
  const elPendientes = document.getElementById('kpiPendientes');

  const meta = document.getElementById('kpiMeta');
  if(meta) meta.textContent = 'Cargando KPIs...';
  try{
    const res = await authFetch('/reportes/dashboard_ejecutivo');
    const data = await safeJson(res);
    if(!res.ok) throw new Error(data?.error || 'Error al cargar KPI');

    const mf = data.metricas_financieras || {};
    const mc = data.metricas_clientes || {};
    const mo = data.metricas_operacionales || {};

    if(elIngresos) elIngresos.textContent = formatSoles(mf.ingresos_mes_actual ?? 0);
    if(elClientes) elClientes.textContent = formatNumber(mc.total_clientes_activos ?? 0);
    if(elAsistencias) elAsistencias.textContent = formatNumber(mo.asistencias_mes_actual ?? 0);
    if(elPendientes) elPendientes.textContent = formatSoles(mf.pagos_pendientes?.monto ?? 0);

    if(meta) meta.textContent = `Última actualización: ${data.fecha_actualizacion ?? new Date().toLocaleString()}`;
  }catch(e){
    console.error('KPIs:', e);
    if(elIngresos) elIngresos.textContent = '—';
    if(elClientes) elClientes.textContent = '—';
    if(elAsistencias) elAsistencias.textContent = '—';
    if(elPendientes) elPendientes.textContent = '—';
    if(meta) meta.textContent = `No se pudieron cargar KPIs: ${e.message}`;
  }
}

// Find expirations in next 7 days using pagos records' fecha_fin
function parseDateYMD(s){ if(!s) return null; const parts = s.split('-'); if(parts.length!==3) return null; return new Date(Number(parts[0]), Number(parts[1])-1, Number(parts[2])); }

async function loadExpiringMemberships(){
  const host = document.getElementById('notificacionesHost');
  if(!host) return;
  host.innerHTML = '<div class="empty">Cargando…</div>';

  try{
    // Fetch upcoming expirations from backend endpoint (efficient)
    const res = await authFetch('/reportes/membresias_por_vencer?days=7');
    const data = await safeJson(res);
    if(!res.ok) throw new Error(data?.error || 'Error al cargar membresías por vencer');
    const list = data.data || [];

    if(list.length===0){ host.innerHTML = '<div class="empty">No hay membresías por vencer en los próximos 7 días.</div>'; return; }

    const today = new Date();
    const rows = list.map(item=>{
      const fecha_fin = parseDateYMD(item.fecha_fin);
      const days = fecha_fin ? Math.ceil((fecha_fin - today)/(1000*60*60*24)) : '?';
      const dd = item.fecha_fin || '';
      return `<div class="notif">
        <div class="notif-left"><strong>${item.cliente_nombre || item.cliente || '—'}</strong><div class="muted">Vence: ${dd} · en ${days} día(s)</div></div>
        <div class="notif-right">${formatSoles(item.monto_pendiente)}</div>
      </div>`;
    }).join('');

    host.innerHTML = rows;
  }catch(e){
    console.error('Expirations:', e);
    host.innerHTML = `<div class="empty">Error cargando notificaciones: ${e.message}</div>`;
  }
}

// Shortcuts can also show counts

async function init(){
  if(!getToken()){ window.location.href='index.html'; return; }
  const ok = await validateToken();
  if(!ok){ window.location.href='index.html'; return; }
  const btnSalir = document.getElementById('btnSalir');
  if(btnSalir) btnSalir.onclick = (e)=>{ e.preventDefault(); setToken(null); logoutAPI(); };

  await Promise.allSettled([
    loadDashboardKPIs(),
    loadExpiringMemberships()
  ]);
}

window.addEventListener('DOMContentLoaded', init);
