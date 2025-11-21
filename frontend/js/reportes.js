import { authFetch, getToken, validateToken, setToken, logoutAPI } from './api.js';

// Paleta de colores agradable y consistente para todos los gráficos
const PALETTE = [
	'#60A5FA', // azul
	'#34D399', // verde
	'#FBBF24', // amarillo/ámbar
	'#FB7185', // rosa claro
	'#A78BFA', // morado
	'#60A5FA', // azul alterno
	'#F97316', // naranja
	'#06B6D4', // cian
	'#10B981', // esmeralda
	'#EF4444'  // rojo
];

function paletteFor(n) {
	// devuelve una lista de n colores rotando sobre PALETTE
	const out = [];
	for (let i = 0; i < n; i++) out.push(PALETTE[i % PALETTE.length]);
	return out;
}

let charts = {};

function numberS(v) { return Number(v || 0); }
function formatSoles(n) { return `S/ ${Number(n || 0).toFixed(2)}`; }
async function safeJson(res) { try { return await res.json(); } catch { return null; } }

async function loadPagosPorMes() {
	const res = await authFetch('/reportes/pagos_por_mes');
	const data = await safeJson(res);
	if (!res.ok) throw new Error(data?.error || 'Error cargando pagos por mes');

	// El endpoint puede devolver lista o {mensaje, datos: []}
	const rows = Array.isArray(data) ? data : (data.datos || []);
	const labels = rows.map(r => r.mes);
	const totals = rows.map(r => numberS(r.total_pagos));
	const count = rows.map(r => numberS(r.cantidad_pagos));

	const ctx = document.getElementById('chPagosMes');
	if (!ctx) return;
	charts.pagosMes && charts.pagosMes.destroy();
	charts.pagosMes = new Chart(ctx, {
		type: 'bar',
		data: {
			labels,
			datasets: [
				{ label: 'Ingresos (S/)', data: totals, backgroundColor: paletteFor(totals.length).map(c => c + '66'), borderColor: PALETTE[0] },
				{ label: 'Pagos', data: count, type: 'line', borderColor: PALETTE[1], backgroundColor: 'transparent', yAxisID: 'y1' }
			]
		},
		options: {
			responsive: true,
			plugins: { legend: { labels: { color: '#F5F5F5' } } },
			scales: {
				x: { ticks: { color: '#F5F5F5' }, grid: { color: '#333' } },
				y: { ticks: { color: '#F5F5F5', callback: v => `S/ ${v}` }, grid: { color: '#333' } },
				y1: { position: 'right', ticks: { color: '#F5F5F5' }, grid: { drawOnChartArea: false } }
			}
		}
	});

	const st = document.getElementById('stPagosMes');
	if (st) st.textContent = `Total meses: ${labels.length} · Ingreso acumulado: ${formatSoles(totals.reduce((a, b) => a + b, 0))}`;
}

async function loadAsistenciasPorPeriodo(fechaInicio, fechaFin) {
	// If no dates provided, call endpoint without params to use backend default
	const qs = [];
	if (fechaInicio) qs.push(`fecha_inicio=${encodeURIComponent(fechaInicio)}`);
	if (fechaFin) qs.push(`fecha_fin=${encodeURIComponent(fechaFin)}`);
	const url = `/reportes/asistencias_por_periodo${qs.length ? ('?' + qs.join('&')) : ''}`;
	const res = await authFetch(url);
	const data = await safeJson(res);
	if (!res.ok) { console.error('Error cargando asistencias por periodo', data); return; }

	const rows = Array.isArray(data) ? data : [];
	const labels = rows.map(r => r.fecha);
	const counts = rows.map(r => numberS(r.cantidad));

	const ctx = document.getElementById('chAsistenciasPeriodo');
	if (!ctx) return;
	charts.asistenciasPeriodo && charts.asistenciasPeriodo.destroy();
	charts.asistenciasPeriodo = new Chart(ctx, {
		type: 'bar',
		data: { labels, datasets: [{ label: 'Asistencias', data: counts, backgroundColor: paletteFor(counts.length).map(c => c + '66'), borderColor: PALETTE[1] }] },
		options: { responsive: true, plugins: { legend: { labels: { color: '#F5F5F5' } } }, scales: { x: { ticks: { color: '#F5F5F5' }, grid: { color: '#333' } }, y: { ticks: { color: '#F5F5F5' }, grid: { color: '#333' } } } }
	});

	const st = document.getElementById('stAsistenciasPeriodo');
	if (st) {
		const total = counts.reduce((a,b)=>a+b,0);
		const desde = fechaInicio || (rows[0] && rows[0].fecha) || '';
		const hasta = fechaFin || (rows[rows.length-1] && rows[rows.length-1].fecha) || '';
		st.textContent = `Rango: ${desde || 'auto'} → ${hasta || 'auto'} · Total asistencias: ${total}`;
	}
}

async function loadIngresosPorMembresia(fechaInicio, fechaFin) {
	const qs = [];
	if (fechaInicio) qs.push(`fecha_inicio=${encodeURIComponent(fechaInicio)}`);
	if (fechaFin) qs.push(`fecha_fin=${encodeURIComponent(fechaFin)}`);
	const url = `/reportes/ingresos_por_membresia${qs.length ? ('?' + qs.join('&')) : ''}`;
	const res = await authFetch(url);
	const data = await safeJson(res);
	if (!res.ok) { console.error('Error cargando ingresos por membresía', data); return; }
	const rows = Array.isArray(data) ? data : [];
	const labels = rows.map(r => r.membresia);
	const totals = rows.map(r => numberS(r.total_ingresos));

	const ctx = document.getElementById('chIngresosMemb');
	if (!ctx) return;
	charts.ingresosMemb && charts.ingresosMemb.destroy();
	charts.ingresosMemb = new Chart(ctx, {
		type: 'bar',
		data: { labels, datasets: [{ label: 'Ingresos (S/)', data: totals, backgroundColor: paletteFor(labels.length).map(c => c + '66'), borderColor: PALETTE[0] }] },
		options: { responsive: true, plugins: { legend: { labels: { color: '#F5F5F5' } } }, scales: { x: { ticks: { color: '#F5F5F5' }, grid: { color: '#333' } }, y: { ticks: { color: '#F5F5F5', callback: v => `S/ ${v}` }, grid: { color: '#333' } } } }
	});

	const st = document.getElementById('stIngresosMemb');
	if (st) st.textContent = `Rango: ${fechaInicio || 'auto'} → ${fechaFin || 'auto'} · Membresías: ${labels.length} · Ingreso total: ${formatSoles(totals.reduce((a, b) => a + b, 0))}`;
}

async function loadMembresiasActivas() {
	// Read date inputs (if present) to filter
	const fi = document.getElementById('membact_fecha_inicio')?.value;
	const ff = document.getElementById('membact_fecha_fin')?.value;
	const qs = [];
	if (fi) qs.push(`fecha_inicio=${encodeURIComponent(fi)}`);
	if (ff) qs.push(`fecha_fin=${encodeURIComponent(ff)}`);
	const url = `/reportes/membresias_activas${qs.length ? ('?' + qs.join('&')) : ''}`;
	const res = await authFetch(url);
	const data = await safeJson(res);
	if (!res.ok) { console.error('Error cargando membresías activas', data); return; }
	const rows = Array.isArray(data) ? data : [];

	const labels = rows.map(r => r.membresia);
	const counts = rows.map(r => numberS(r.cantidad_clientes));
	const ctx = document.getElementById('chMembActivas');
	if (!ctx) return;
	charts.membActivas && charts.membActivas.destroy();
	charts.membActivas = new Chart(ctx, {
		type: 'bar',
		data: { labels, datasets: [{ label: 'Clientes', data: counts, backgroundColor: paletteFor(counts.length).map(c => c + '66'), borderColor: PALETTE[0] }] },
		options: { responsive: true, plugins: { legend: { labels: { color: '#F5F5F5' } } }, scales: { x: { ticks: { color: '#F5F5F5' }, grid: { color: '#333' } }, y: { ticks: { color: '#F5F5F5' }, grid: { color: '#333' } } } }
	});

	const st = document.getElementById('stMembActivas');
	if (st) st.textContent = `Rango: ${fi || 'auto'} → ${ff || 'auto'} · Total clientes: ${counts.reduce((a, b) => a + b, 0)}`;
}

async function loadMembresiasPorPrecio() {
	const res = await authFetch('/reportes/membresias_por_precio');
	const data = await safeJson(res);
	if (!res.ok) { console.error('Error cargando membresías por precio', data); return; }

	const rows = Array.isArray(data) ? data : [];
	const labels = rows.map(r => r.nombre);
	const precios = rows.map(r => Number(r.precio || 0));

	const ctx = document.getElementById('chMembPorPrecio');
	if (!ctx) return;
	charts.membPorPrecio && charts.membPorPrecio.destroy();
	charts.membPorPrecio = new Chart(ctx, {
		type: 'bar',
		data: { labels, datasets: [{ label: 'Precio (S/)', data: precios, backgroundColor: paletteFor(labels.length).map(c => c + '66'), borderColor: PALETTE[0] }] },
		options: { responsive: true, plugins: { legend: { labels: { color: '#F5F5F5' } } }, scales: { x: { ticks: { color: '#F5F5F5' }, grid: { color: '#333' } }, y: { ticks: { color: '#F5F5F5' }, grid: { color: '#333' } } } }
	});

	const st = document.getElementById('stMembPorPrecio');
	if (st) {
		if (precios.length === 0) {
			st.textContent = `Sin datos`;
		} else {
			const minP = Math.min(...precios);
			const maxP = Math.max(...precios);
			st.textContent = `Membresías: ${labels.length} · Precio mínimo: S/ ${minP.toFixed(2)} · Precio máximo: S/ ${maxP.toFixed(2)}`;
		}
	}
}

async function loadClientesNuevos() {
	// Support fecha_inicio/fecha_fin via the date inputs
	const fi = document.getElementById('cli_fecha_inicio')?.value;
	const ff = document.getElementById('cli_fecha_fin')?.value;
	const qs = [];
	if (fi) qs.push(`fecha_inicio=${encodeURIComponent(fi)}`);
	if (ff) qs.push(`fecha_fin=${encodeURIComponent(ff)}`);
	const url = `/reportes/clientes_nuevos_por_mes${qs.length ? ('?' + qs.join('&')) : ''}`;
	const res = await authFetch(url);
	const data = await safeJson(res);
	if (!res.ok) { console.error('Error cargando clientes nuevos', data); return; }
	const rows = Array.isArray(data) ? data : [];
	const labels = rows.map(r => r.mes);
	const counts = rows.map(r => numberS(r.total_clientes_nuevos));
	const ctx = document.getElementById('chClientesNuevos');
	if (!ctx) return;
	charts.clientesNuevos && charts.clientesNuevos.destroy();
	charts.clientesNuevos = new Chart(ctx, { type: 'line', data: { labels, datasets: [{ label: 'Clientes nuevos', data: counts, borderColor: PALETTE[4], backgroundColor: 'transparent' }] }, options: { plugins: { legend: { labels: { color: '#F5F5F5' } } }, scales: { x: { ticks: { color: '#F5F5F5' }, grid: { color: '#333' } }, y: { ticks: { color: '#F5F5F5' }, grid: { color: '#333' } } } } });

	const st = document.getElementById('stClientesNuevos');
	if (st) st.textContent = `Rango: ${fi || 'auto'} → ${ff || 'auto'} · Meses: ${labels.length} · Nuevos: ${counts.reduce((a, b) => a + b, 0)}`;
}

async function loadPagosPendientes() {
	const host = document.getElementById('tbPendientesHost');
	if (!host) return;
	host.innerHTML = '<div class="empty">Cargando…</div>';
	const res = await authFetch('/reportes/pagos_pendientes');
	const data = await safeJson(res);
	if (!res.ok) { host.innerHTML = `<div class="empty">${data?.error || 'Error al cargar'}</div>`; return; }
	const rows = Array.isArray(data) ? data : [];
	if (rows.length === 0) { host.innerHTML = '<div class="empty">Sin pagos pendientes 🎉</div>'; return; }
	const html = `
		<table>
			<thead><tr><th>Cliente</th><th>Documento</th><th>Monto</th><th>Fecha</th><th>Estado</th></tr></thead>
			<tbody>
				${rows.map(r => `<tr><td>${r.cliente}</td><td>${r.numero_documento}</td><td>${formatSoles(r.monto)}</td><td>${r.fecha_pago || ''}</td><td>${r.estado}</td></tr>`).join('')}
			</tbody>
		</table>`;
	host.innerHTML = html;
}

/* ----------------------- Export helpers (CSV / PDF) ----------------------- */
function escapeCsvCell(v) {
	if (v === null || v === undefined) return '';
	const s = String(v);
	if (s.includes(',') || s.includes('"') || s.includes('\n')) {
		return '"' + s.replace(/"/g, '""') + '"';
	}
	return s;
}

function exportToCSV(filename, headers, rows) {
	const headerLine = headers.map(escapeCsvCell).join(',');
	const body = rows.map(r => r.map(escapeCsvCell).join(',')).join('\n');
	const csv = headerLine + '\n' + body;
	const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = filename;
	document.body.appendChild(a);
	a.click();
	a.remove();
	URL.revokeObjectURL(url);
}

function exportToPDF(filename, headers, rows) {
	try {
		const jsPDFGlobal = window.jspdf || window.jspdf; // UMD exposes window.jspdf
		const jsPDFCtor = jsPDFGlobal && jsPDFGlobal.jsPDF ? jsPDFGlobal.jsPDF : window.jsPDF;
		if (!jsPDFCtor) {
			alert('jsPDF no está disponible en este entorno.');
			return;
		}
		const doc = new jsPDFCtor({ orientation: 'landscape' });
		// AutoTable registers as doc.autoTable
		if (doc.autoTable) {
			doc.autoTable({ head: [headers], body: rows });
		} else if (typeof doc['autoTable'] === 'function') {
			doc.autoTable({ head: [headers], body: rows });
		} else {
			// Fallback: render plain text
			doc.text(headers.join(' | '), 10, 10);
			let y = 20;
			rows.forEach(r => {
				doc.text(r.join(' | '), 10, y);
				y += 8;
			});
		}
		doc.save(filename);
	} catch (e) {
		console.error('Error exportando a PDF', e);
		alert('Error generando PDF: ' + e.message);
	}
}

async function fetchAndFormatData(type) {
	// Returns { headers: [], rows: [[]] }
	try {
		if (type === 'asistencias') {
			const fi = document.getElementById('asist_fecha_inicio').value;
			const ff = document.getElementById('asist_fecha_fin').value;
			const qs = [];
			if (fi) qs.push(`fecha_inicio=${encodeURIComponent(fi)}`);
			if (ff) qs.push(`fecha_fin=${encodeURIComponent(ff)}`);
			const url = `/reportes/asistencias_por_periodo${qs.length ? ('?' + qs.join('&')) : ''}`;
			const res = await authFetch(url);
			const data = await safeJson(res);
			const rows = (Array.isArray(data) ? data : []).map(r => [r.fecha || '', r.cantidad || 0]);
			return { headers: ['Fecha', 'Asistencias'], rows };
		}
		if (type === 'ingresos') {
			const fi = document.getElementById('ing_fecha_inicio')?.value;
			const ff = document.getElementById('ing_fecha_fin')?.value;
			const qs = [];
			if (fi) qs.push(`fecha_inicio=${encodeURIComponent(fi)}`);
			if (ff) qs.push(`fecha_fin=${encodeURIComponent(ff)}`);
			const url = `/reportes/ingresos_por_membresia${qs.length ? ('?' + qs.join('&')) : ''}`;
			const res = await authFetch(url);
			const data = await safeJson(res);
			const rows = (Array.isArray(data) ? data : []).map(r => [r.membresia || '', (r.total_ingresos != null) ? Number(r.total_ingresos).toFixed(2) : '0.00']);
			return { headers: ['Membresía', 'Ingreso (S/)'], rows };
		}
		if (type === 'membresias_activas') {
			const fi = document.getElementById('membact_fecha_inicio')?.value;
			const ff = document.getElementById('membact_fecha_fin')?.value;
			const qs = [];
			if (fi) qs.push(`fecha_inicio=${encodeURIComponent(fi)}`);
			if (ff) qs.push(`fecha_fin=${encodeURIComponent(ff)}`);
			const url = `/reportes/membresias_activas${qs.length ? ('?' + qs.join('&')) : ''}`;
			const res = await authFetch(url);
			const data = await safeJson(res);
			const rows = (Array.isArray(data) ? data : []).map(r => [r.membresia || '', (r.precio != null) ? Number(r.precio).toFixed(2) : '0.00', r.duracion_dias || '', r.cantidad_clientes || 0]);
			return { headers: ['Membresía', 'Precio (S/)', 'Duración (días)', 'Clientes'], rows };
		}
		if (type === 'membresias_precio') {
			const res = await authFetch('/reportes/membresias_por_precio');
			const data = await safeJson(res);
			const rows = (Array.isArray(data) ? data : []).map(r => [r.nombre || '', (r.precio != null) ? Number(r.precio).toFixed(2) : '0.00']);
			return { headers: ['Membresía', 'Precio (S/)'], rows };
		}
		if (type === 'clientes_nuevos') {
			const fi = document.getElementById('cli_fecha_inicio')?.value;
			const ff = document.getElementById('cli_fecha_fin')?.value;
			const qs = [];
			if (fi) qs.push(`fecha_inicio=${encodeURIComponent(fi)}`);
			if (ff) qs.push(`fecha_fin=${encodeURIComponent(ff)}`);
			const url = `/reportes/clientes_nuevos_por_mes${qs.length ? ('?' + qs.join('&')) : ''}`;
			const res = await authFetch(url);
			const data = await safeJson(res);
			const rows = (Array.isArray(data) ? data : []).map(r => [r.mes || '', r.total_clientes_nuevos || 0]);
			return { headers: ['Mes', 'Nuevos'], rows };
		}
		return { headers: [], rows: [] };
	} catch (e) {
		console.error('Error obteniendo datos para exportar', e);
		return { headers: [], rows: [] };
	}
}

// Wire export buttons after DOM is ready (listeners added below in DOMContentLoaded)


document.addEventListener('DOMContentLoaded', async () => {
	// Guard de autenticación
	if (!getToken()) { window.location.href = 'index.html'; return; }
	const ok = await validateToken();
	if (!ok) { window.location.href = 'index.html'; return; }
	const btnSalir = document.getElementById('btnSalir') || document.getElementById('logoutButton');
	if (btnSalir) btnSalir.onclick = (e) => { e.preventDefault(); setToken(null); logoutAPI(); };

	// Set sensible defaults for the date inputs (last 4 months) BEFORE initial load
	try {
		const hoy = new Date();
		const hoyStr = hoy.toISOString().slice(0,10);
		const ini = new Date(hoy.getFullYear(), hoy.getMonth()-3, 1).toISOString().slice(0,10);
		// asistencias
		const finAsist = document.getElementById('asist_fecha_fin');
		const iniAsist = document.getElementById('asist_fecha_inicio');
		if (finAsist) finAsist.value = hoyStr;
		if (iniAsist) iniAsist.value = ini;
		// others
		[document.getElementById('ing_fecha_fin'), document.getElementById('membact_fecha_fin'), document.getElementById('cli_fecha_fin')].forEach(el => { if (el) el.value = hoyStr; });
		[document.getElementById('ing_fecha_inicio'), document.getElementById('membact_fecha_inicio'), document.getElementById('cli_fecha_inicio')].forEach(el => { if (el) el.value = ini; });
	} catch(e){/* ignore */}

	try {
		await Promise.all([
			loadAsistenciasPorPeriodo(),
			loadIngresosPorMembresia(),
			loadMembresiasActivas(),
			loadMembresiasPorPrecio(),
			loadClientesNuevos(),
			loadPagosPendientes()
		]);
	} catch (e) {
		console.error('Error cargando reportes:', e);
	}
	// Wire up the asistencia date controls
	const btn = document.getElementById('btnAsistActualizar');
	if (btn) {
		btn.onclick = async () => {
			const fi = document.getElementById('asist_fecha_inicio').value;
			const ff = document.getElementById('asist_fecha_fin').value;
			await loadAsistenciasPorPeriodo(fi || null, ff || null);
		};
	}

	// Wire update buttons for the new date controls
	const btnIng = document.getElementById('btnIngActualizar');
	if (btnIng) {
		btnIng.onclick = async () => {
			const fi = document.getElementById('ing_fecha_inicio').value || null;
			const ff = document.getElementById('ing_fecha_fin').value || null;
			await loadIngresosPorMembresia(fi, ff);
		};
	}
	const btnMembAct = document.getElementById('btnMembActActualizar');
	if (btnMembAct) {
		btnMembAct.onclick = async () => {
			const fi = document.getElementById('membact_fecha_inicio').value || null;
			const ff = document.getElementById('membact_fecha_fin').value || null;
			// loader reads inputs directly
			await loadMembresiasActivas();
		};
	}
	const btnCli = document.getElementById('btnCliActualizar');
	if (btnCli) {
		btnCli.onclick = async () => {
			const fi = document.getElementById('cli_fecha_inicio').value || null;
			const ff = document.getElementById('cli_fecha_fin').value || null;
			// loader reads inputs directly
			await loadClientesNuevos();
		};
	}

	// Wire export buttons (CSV / PDF) for each card
	try {
		const exportBtns = document.querySelectorAll('.export-btn');
		exportBtns.forEach(btn => {
			btn.addEventListener('click', async (ev) => {
				const type = btn.dataset.type;
				const format = btn.dataset.format; // 'csv' or 'pdf'
				const { headers, rows } = await fetchAndFormatData(type);
				if (!rows || rows.length === 0) {
					alert('No hay datos para exportar');
					return;
				}
				const dateTag = new Date().toISOString().slice(0,10);
				const ext = (format === 'csv') ? 'csv' : 'pdf';
				const filename = `${type}_${dateTag}.${ext}`;
				if (format === 'csv') exportToCSV(filename, headers, rows);
				else exportToPDF(filename, headers, rows);
			});
		});
	} catch (e) { console.error('Error wiring export buttons', e); }
});

