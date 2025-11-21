// Clientes module - listado, creación, edición y eliminación
import { authFetch, getToken, setToken, logoutAPI, validateToken } from './api.js';

// Estado de paginación/búsqueda
let page = 1;
let size = 10;
let search = '';

// Referencias del DOM (se resolverán tras DOMContentLoaded)
let qEl, btnBuscar, btnSalir, rows, pageInfo, prev, next, meta, btnNuevo;
let clientModal, modalTitle, clientForm, btnCancel, idClienteInput, membresiaSelect;

// Utilidad segura para parsear JSON
async function safeJson(res) {
	try { return await res.json(); } catch { return null; }
}

// Cargar y renderizar resumen de clientes (KPI)
async function loadClientesResumen() {
	const host = document.getElementById('clientesSummaryHost');
	if (!host) return;
	host.innerHTML = '<div class="kpi">Cargando...</div>';
	try {
		const res = await authFetch('/reportes/clientes_resumen');
		if (!res.ok) throw new Error((await safeJson(res))?.message || 'HTTP ' + res.status);
		const data = await res.json();

		host.innerHTML = `
			<a class="shortcut" href="#" title="Total de clientes" aria-label="Total de clientes">
				<div class="icon">👥</div>
				<div class="text"> 
					<div class="kpi-value">${data.total}</div>
					<div class="kpi-label">Total</div>
				</div>
			</a>
			<a class="shortcut" href="#" title="Clientes VIP" aria-label="Clientes VIP">
				<div class="icon">💎</div>
				<div class="text"> 
					<div class="kpi-value">${data.vip}</div>
					<div class="kpi-label">VIP</div>
				</div>
			</a>
			<a class="shortcut" href="#" title="Clientes Básica" aria-label="Clientes Básica">
				<div class="icon">🔰</div>
				<div class="text"> 
					<div class="kpi-value">${data.basica}</div>
					<div class="kpi-label">Básica</div>
				</div>
			</a>
			<a class="shortcut" href="#" title="Registrados último mes" aria-label="Registrados último mes">
				<div class="icon">🆕</div>
				<div class="text"> 
					<div class="kpi-value">${data.registrados_ultimo_mes}</div>
					<div class="kpi-label">Nuevos (últ. mes)</div>
				</div>
			</a>
		`;
	} catch (err) {
		console.error('Error cargando resumen de clientes:', err);
		host.innerHTML = '<div class="empty">No se pudo cargar el resumen</div>';
	}
}

// Abrir/Cerrar modal
function openModal(mode, client = null) {
	if (!clientModal || !clientForm) return;
	clientForm.reset();

	if (mode === 'add') {
		modalTitle && (modalTitle.textContent = 'Nuevo Cliente');
		idClienteInput && (idClienteInput.value = '');
	} else if (mode === 'edit' && client) {
		modalTitle && (modalTitle.textContent = 'Editar Cliente');

		const elementos = {
			id_cliente: document.getElementById('id_cliente'),
			nombre: document.getElementById('nombre'),
			apellido_paterno: document.getElementById('apellido_paterno'),
			apellido_materno: document.getElementById('apellido_materno'),
			tipo_documento: document.getElementById('tipo_documento'),
			numero_documento: document.getElementById('numero_documento'),
			correo: document.getElementById('correo'),
			telefono: document.getElementById('telefono'),
			id_membresia: document.getElementById('id_membresia')
		};

		if (elementos.id_cliente) elementos.id_cliente.value = client.id_cliente ?? '';
		if (elementos.nombre) elementos.nombre.value = client.nombre ?? '';
		if (elementos.apellido_paterno) elementos.apellido_paterno.value = client.apellido_paterno ?? '';
		if (elementos.apellido_materno) elementos.apellido_materno.value = client.apellido_materno ?? '';
		if (elementos.tipo_documento) elementos.tipo_documento.value = client.tipo_documento ?? 'DNI';
		if (elementos.numero_documento) elementos.numero_documento.value = client.numero_documento ?? '';
		if (elementos.correo) elementos.correo.value = client.correo ?? '';
		if (elementos.telefono) elementos.telefono.value = client.telefono ?? '';
		if (elementos.id_membresia) elementos.id_membresia.value = client.id_membresia ?? '';
	}

	clientModal.classList.add('active');
}

function closeModal() {
	if (!clientModal) return;
	clientModal.classList.remove('active');
}

// Cargar membresías para el select
async function loadMembresias() {
	if (!membresiaSelect) return;
	try {
		const res = await authFetch('/membresias/');
		if (!res.ok) throw new Error((await safeJson(res))?.message || 'HTTP ' + res.status);
		const data = await res.json();
		const list = Array.isArray(data) ? data : (data.data || data.membresias || []);

		membresiaSelect.innerHTML = '<option value="">Ninguna</option>';
		list.forEach(m => {
			if (!m || !m.id_membresia) return;
			const opt = document.createElement('option');
			opt.value = m.id_membresia;
			opt.textContent = `${m.nombre} ${m.precio ? `(S/ ${Number(m.precio).toFixed(2)})` : ''}`;
			membresiaSelect.appendChild(opt);
		});
	} catch (e) {
		console.error('Error cargando membresías:', e);
		membresiaSelect.innerHTML = '<option value="">Error al cargar</option>';
	}
}

// Renderizar filas de clientes
function renderRows(list) {
	if (!rows) return;
	if (!Array.isArray(list) || list.length === 0) {
		rows.innerHTML = '<tr><td colspan="7">Sin resultados</td></tr>';
		return;
	}

	rows.innerHTML = list.map(c => `
		<tr>
			<td>${c.id_cliente}</td>
			<td>${c.tipo_documento || ''} ${c.numero_documento || ''}</td>
			<td>${[c.nombre, c.apellido_paterno, c.apellido_materno].filter(Boolean).join(' ')}</td>
			<td>${c.correo || ''}</td>
			<td>${c.telefono || ''}</td>
			<td>${c.nombre_membresia || 'Ninguna'}</td>
			<td class="actions-cell">
				<button class="btn icon edit-btn" data-id="${c.id_cliente}" title="Editar">✏️</button>
				<button class="btn icon danger delete-btn" data-id="${c.id_cliente}" title="Eliminar">🗑️</button>
			</td>
		</tr>
	`).join('');
}

// Cargar lista (paginada + búsqueda)
async function loadList() {
	if (!rows || !pageInfo) return;
	rows.innerHTML = '<tr><td colspan="7">Cargando...</td></tr>';
	try {
		const params = new URLSearchParams();
		params.set('page', String(page));
		params.set('size', String(size));
		if (search && search.trim()) params.set('search', search.trim());

		const res = await authFetch(`/clientes/?${params.toString()}`);
		if (!res.ok) throw new Error((await safeJson(res))?.message || `HTTP ${res.status}`);
		const data = await res.json();

		const list = Array.isArray(data) ? data : (data.data || []);
		const total = data.total ?? (data.pagination?.total ?? list.length);
		const pages = data.pages ?? (data.pagination?.pages ?? 1);

		renderRows(list);

		pageInfo.textContent = Array.isArray(data)
			? `Total: ${total}`
			: `Página ${page} de ${pages}`;
		meta && (meta.textContent = search ? `Mostrando resultados para: "${search}"` : '');
		if (prev) prev.disabled = page <= 1;
		if (next) next.disabled = page >= pages;
	} catch (e) {
		console.error('Error en loadList:', e);
		rows.innerHTML = `<tr><td colspan="7">Error cargando clientes: ${e.message || ''}</td></tr>`;
	}
}

// Obtener un cliente por ID
async function fetchCliente(id) {
	const res = await authFetch(`/clientes/${id}`);
	if (!res.ok) throw new Error((await safeJson(res))?.message || 'Error al obtener cliente');
	return await res.json();
}

function normalizeTipoDocumento(value) {
	const v = (value || '').toUpperCase().trim();
	if (v === 'C.E.' || v === 'CE' || v === 'CARNET DE EXTRANJERÍA' || v === 'CARNET DE EXTRANJERIA') return 'CE';
	if (v === 'RUC') return 'RUC';
	if (v === 'DNI') return 'DNI';
	if (v === 'PASAPORTE') return 'CE'; // Mapeo conservador a CE para cumplir constraint
	return 'DNI';
}

// Guardar (crear o actualizar)
async function saveCliente(e) {
	e.preventDefault();
	const id = idClienteInput ? idClienteInput.value : '';
	const method = id ? 'PUT' : 'POST';
	const url = id ? `/clientes/${id}` : '/clientes/';

	const body = {
		nombre: (document.getElementById('nombre')?.value || '').trim(),
		apellido_paterno: (document.getElementById('apellido_paterno')?.value || '').trim(),
		apellido_materno: (document.getElementById('apellido_materno')?.value || '').trim(),
		tipo_documento: normalizeTipoDocumento(document.getElementById('tipo_documento')?.value || 'DNI'),
		numero_documento: (document.getElementById('numero_documento')?.value || '').trim(),
		correo: (document.getElementById('correo')?.value || '').trim(),
		telefono: (document.getElementById('telefono')?.value || '').trim(),
		id_membresia: (document.getElementById('id_membresia')?.value || '') || null,
	};

	try {
		const res = await authFetch(url, {
			method,
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(body)
		});
		if (!res.ok) throw new Error((await safeJson(res))?.message || 'Error al guardar');
		closeModal();
		await loadList();
		alert(`Cliente ${id ? 'actualizado' : 'creado'} con éxito.`);
	} catch (err) {
		console.error(err);
		alert('No se pudo guardar el cliente: ' + err.message);
	}
}

// Delegación de eventos para Editar/Eliminar
function onRowsClick(e) {
	let btn = e.target;
	while (btn && btn.tagName !== 'BUTTON' && btn !== rows) {
		btn = btn.parentElement;
	}
	if (!btn || btn.tagName !== 'BUTTON') return;

	const id = btn.dataset.id;
	if (!id) return;

	if (btn.classList.contains('edit-btn')) {
		(async () => {
			try {
				const client = await fetchCliente(id);
				openModal('edit', client);
			} catch (err) {
				console.error('Error al editar:', err);
				alert('No se pudieron cargar los datos del cliente: ' + err.message);
			}
		})();
	} else if (btn.classList.contains('delete-btn')) {
		(async () => {
			try {
				const res1 = await authFetch(`/clientes/${id}`, { method: 'DELETE' });
				const data1 = await safeJson(res1);

				if (data1 && data1.success === false && data1.instrucciones) {
					const c = data1.cliente || {};
					const confirmMessage = `¿Eliminar cliente?\n\n` +
						`• Nombre: ${c.nombre_completo || ''}\n` +
						`• Documento: ${c.numero_documento || ''}\n` +
						`• Email: ${c.correo || 'No registrado'}\n` +
						`• Teléfono: ${c.telefono || 'No registrado'}\n\n` +
						`Esta acción no se puede deshacer.`;

					if (window.confirm(confirmMessage)) {
						const res2 = await authFetch(`/clientes/${id}?confirmar=true`, { method: 'DELETE' });
						const data2 = await safeJson(res2);
						if (data2 && data2.success) {
							await loadList();
							alert(data2.message || 'Cliente eliminado con éxito.');
						} else {
							alert((data2 && data2.message) || 'No se pudo eliminar el cliente.');
						}
					}
				} else if (data1 && data1.success) {
					await loadList();
					alert(data1.message || 'Cliente eliminado con éxito.');
				} else {
					alert((data1 && data1.message) || 'Error al procesar la eliminación.');
				}
			} catch (err) {
				console.error('Error al eliminar:', err);
				alert('No se pudo eliminar el cliente.');
			}
		})();
	}
}

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
	// Resolver elementos del DOM
	qEl = document.getElementById('q');
	btnBuscar = document.getElementById('btnBuscar');
	btnSalir = document.getElementById('btnSalir') || document.getElementById('logoutButton');
	rows = document.getElementById('rows');
	pageInfo = document.getElementById('pageInfo');
	prev = document.getElementById('prev');
	next = document.getElementById('next');
	meta = document.getElementById('meta');
	btnNuevo = document.getElementById('btnNuevo');

	clientModal = document.getElementById('clientModal');
	modalTitle = document.getElementById('modalTitle');
	clientForm = document.getElementById('clientForm');
	btnCancel = document.getElementById('btnCancel');
	idClienteInput = document.getElementById('id_cliente');
	membresiaSelect = document.getElementById('id_membresia');

	// Proteger la página
	const token = getToken();
	if (!token) {
		window.location.href = 'index.html';
		return;
	}
	const isAuth = await validateToken();
	if (!isAuth) {
		window.location.href = 'index.html';
		return;
	}

	// Eventos globales
	if (btnSalir) {
		btnSalir.onclick = (e) => { e.preventDefault(); setToken(null); logoutAPI(); };
	}
	if (btnBuscar && qEl) {
		btnBuscar.onclick = () => { search = (qEl.value || '').trim(); page = 1; loadList(); };
	}
	if (qEl) {
		qEl.onkeypress = (e) => { if (e.key === 'Enter') { search = (qEl.value || '').trim(); page = 1; loadList(); } };
	}
	if (prev) {
		prev.onclick = () => { if (page > 1) { page--; loadList(); } };
	}
	if (next) {
		next.onclick = () => { page++; loadList(); };
	}
	if (btnNuevo) {
		btnNuevo.onclick = () => openModal('add');
	}
	if (btnCancel) {
		btnCancel.onclick = closeModal;
	}
	if (clientModal) {
		clientModal.onclick = (e) => { if (e.target === clientModal) closeModal(); };
	}
	if (clientForm) {
		clientForm.onsubmit = saveCliente;
	}
	if (rows) {
		rows.onclick = onRowsClick;
	}

	// Cargas iniciales
	await loadMembresias();
	await loadClientesResumen();
	await loadList();
});

