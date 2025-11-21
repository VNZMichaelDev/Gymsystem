import { authFetch, getToken, setToken, validateToken, logoutAPI } from './api.js';

// Estado global
let currentPage = 1;
let totalPages = 1;
let currentPaymentInfo = null;

// Refs DOM
let formSection, formPago, btnNuevoPago, btnCancelar, selectCliente, btnCargarInfo;
let paymentInfo, montoPagadoInput, quedaraDebiendoInput, msg;
let searchInput, filtroClienteInput, btnBuscar, btnLimpiar, tableBody, prevBtn, nextBtn, pageInfo;

// API helpers
async function safeJson(res) { try { return await res.json(); } catch { return null; } }

// UI helpers
function show(el) { el && el.classList.remove('hidden'); }
function hide(el) { el && el.classList.add('hidden'); }

// Cargar y renderizar resumen KPIs de pagos
async function loadPagosResumen() {
	const host = document.getElementById('pagosSummaryHost');
	if (!host) return;
	host.innerHTML = '<div class="shortcut">Cargando...</div>';
	try {
		const res = await authFetch('/reportes/pagos_resumen');
		if (!res.ok) throw new Error((await safeJson(res))?.message || 'HTTP ' + res.status);
		const data = await res.json();
		host.innerHTML = `
			<a class="shortcut" href="#" title="Pagos realizados" aria-label="Pagos realizados">
				<div class="icon">💳</div>
				<div class="text">
					<div class="kpi-value">${data.pagos_realizados}</div>
					<div class="kpi-label">Pagos realizados</div>
				</div>
			</a>
			<a class="shortcut" href="#" title="Membresías usadas" aria-label="Membresías usadas">
				<div class="icon">🎫</div>
				<div class="text">
					<div class="kpi-value">${data.membresias_usadas}</div>
					<div class="kpi-label">Membresías usadas</div>
				</div>
			</a>
			<a class="shortcut" href="#" title="Clientes que ya pagaron" aria-label="Clientes que ya pagaron">
				<div class="icon">👤</div>
				<div class="text">
					<div class="kpi-value">${data.clientes_que_pagaron}</div>
					<div class="kpi-label">Clientes que pagaron</div>
				</div>
			</a>
			<a class="shortcut" href="#" title="Clientes sin pagos" aria-label="Clientes sin pagos">
				<div class="icon">🚫</div>
				<div class="text">
					<div class="kpi-value">${data.clientes_sin_pagos}</div>
					<div class="kpi-label">Sin pagos</div>
				</div>
			</a>
			<a class="shortcut" href="#" title="Clientes con deuda" aria-label="Clientes con deuda">
				<div class="icon">⚠️</div>
				<div class="text">
					<div class="kpi-value">${data.clientes_con_deuda}</div>
					<div class="kpi-label">Con deuda</div>
				</div>
			</a>
		`;
	} catch (e) {
		console.error('Error cargando resumen de pagos:', e);
		host.innerHTML = '<div class="empty">No se pudo cargar el resumen</div>';
	}
}

// Render tabla
function renderTabla(pagos) {
	if (!tableBody) return;
	if (!Array.isArray(pagos) || pagos.length === 0) {
		tableBody.innerHTML = '<tr><td colspan="8" class="text-center">No se encontraron pagos</td></tr>';
		return;
	}
	tableBody.innerHTML = pagos.map(pago => {
		const estadoBadge = pago.estado === 'Pagado' ? 'success' : pago.estado === 'Pendiente' ? 'warning' : 'danger';
		return `
			<tr>
				<td>${pago.id_pago}</td>
				<td>${pago.cliente_nombre || 'N/A'}</td>
				<td>${pago.membresia_nombre || 'N/A'}</td>
				<td>S/ ${Number(pago.monto_total ?? 0).toFixed(2)}</td>
				<td>S/ ${Number(pago.monto_pagado ?? 0).toFixed(2)}</td>
				<td>S/ ${Number(pago.monto_pendiente ?? 0).toFixed(2)}</td>
				<td>${pago.fecha_pago || ''}</td>
				<td>
					<div class="action-buttons">
						<span class="badge badge-${estadoBadge}">${pago.estado}</span>
						${pago.comprobante ? `
							<button class="btn btn-info btn-sm" onclick="verComprobante(${pago.id_pago})" title="Ver comprobante">
								<svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
									<path d="M10.5 8.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/>
									<path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8zm8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z"/>
								</svg>
							</button>` : ''}
						<button class="btn btn-warning btn-sm" onclick="editarPago(${pago.id_pago})" title="Editar pago">
							<svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
								<path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708L4.707 15H1v-3.707L12.146.146zM2 12.293l1.146-1.147a.5.5 0 0 1 .708.708L2.707 13H2v-.707z"/>
							</svg>
						</button>
						<button class="btn btn-danger btn-sm" onclick="eliminarPago(${pago.id_pago})" title="Eliminar pago">
							<svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
								<path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
								<path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
							</svg>
						</button>
					</div>
				</td>
			</tr>
		`;
	}).join('');
}

function renderPagination(total, size, page) {
	const totalItems = Number(total) || 0;
	const itemsPerPage = Number(size) || 10;
	totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
	currentPage = Math.min(Math.max(1, page), totalPages);

	const startItem = totalItems === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1;
	const endItem = Math.min(currentPage * itemsPerPage, totalItems);
	if (pageInfo) pageInfo.textContent = `Mostrando ${startItem}-${endItem} de ${totalItems} pagos`;
	if (prevBtn) prevBtn.disabled = currentPage <= 1;
	if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
}

// Cargar clientes para el select
async function loadClientes() {
	try {
		const res = await authFetch('/clientes/?size=1000');
		const data = await res.json();
		const clientes = data.data || [];
		if (selectCliente) {
			selectCliente.innerHTML = '<option value="">Seleccionar cliente...</option>';
			clientes.forEach(c => {
				const opt = document.createElement('option');
				opt.value = c.id_cliente;
				opt.textContent = `${c.nombre_completo} - ${c.numero_documento}`;
				selectCliente.appendChild(opt);
			});
		}
	} catch (e) {
		if (msg) msg.textContent = 'Error al cargar clientes';
	}
}

// Cargar info de pago para cliente seleccionado
async function loadPaymentInfo() {
	const clienteId = selectCliente?.value;
	if (!clienteId) { alert('Selecciona un cliente'); return; }
	try {
		if (msg) msg.textContent = 'Cargando información...';
		const res = await authFetch(`/pagos/cliente/${clienteId}/info`);
		const data = await res.json();
		if (!res.ok) throw new Error(data?.error || 'No se pudo obtener la información');

		currentPaymentInfo = data;
		document.getElementById('membresia_nombre').value = data.membresia.nombre;
		document.getElementById('monto_total').value = `S/ ${Number(data.pago_info.monto_total).toFixed(2)}`;
		document.getElementById('total_pagado').value = `S/ ${Number(data.pago_info.total_pagado).toFixed(2)}`;
		document.getElementById('monto_pendiente').value = `S/ ${Number(data.pago_info.monto_pendiente).toFixed(2)}`;
		document.getElementById('fecha_inicio').value = data.pago_info.fecha_inicio;
		document.getElementById('fecha_fin').value = data.pago_info.fecha_fin;
		document.getElementById('tiempo_restante').value = `${data.pago_info.dias_restantes} días`;
		montoPagadoInput.max = data.pago_info.monto_pendiente;
		montoPagadoInput.value = '';
		quedaraDebiendoInput.value = `S/ ${Number(data.pago_info.monto_pendiente).toFixed(2)}`;
		show(paymentInfo);
		if (msg) msg.textContent = '';
	} catch (e) {
		if (msg) msg.textContent = 'Error: ' + e.message;
		hide(paymentInfo);
	}
}

// Listar pagos con búsqueda/filtro/paginación
async function loadPagos(page = 1, search = '') {
	const size = 10;
	const offset = (page - 1) * size;
	const clienteId = filtroClienteInput?.value?.trim() || '';
	let url = `/pagos/?size=${size}&offset=${offset}`;
	if (search) url += `&search=${encodeURIComponent(search)}`;
	if (clienteId) url += `&cliente_id=${encodeURIComponent(clienteId)}`;
	try {
		const res = await authFetch(url);
		const data = await res.json();
		if (!res.ok) throw new Error(data?.error || 'Error al cargar pagos');
		const list = data.data || [];
		const total = (data.pagination && typeof data.pagination.total === 'number') ? data.pagination.total : list.length;
		renderTabla(list);
		renderPagination(total, size, page);
	} catch (e) {
		if (tableBody) tableBody.innerHTML = `<tr><td colspan="8" class="text-center">${e.message}</td></tr>`;
	}
}

// Ver comprobante de pago (modal con blob seguro)
window.verComprobante = async function(idPago) {
	const modal = document.getElementById('comprobanteModal');
	const modalContent = document.getElementById('modalContent');
	const btnCerrarModal = document.getElementById('btnCerrarModal');
	if (!(modal && modalContent)) return;
	try {
		const res = await authFetch(`/pagos/${idPago}/comprobante`);
		if (!res.ok) {
			const err = await safeJson(res);
			alert('No se pudo cargar el comprobante: ' + (err?.error || res.status));
			return;
		}
		const blob = await res.blob();
		const url = URL.createObjectURL(blob);
		const mime = blob.type || '';
		let contentHtml = '';
		if (mime.startsWith('image/')) {
			contentHtml = `<div class="comprobante-viewer"><img src="${url}" alt="Comprobante" style="max-width: 100%; height: auto; border-radius: 0.5rem;"></div>`;
		} else if (mime === 'application/pdf') {
			contentHtml = `<iframe src="${url}" style="width:100%;height:70vh;border:0;border-radius:8px;"></iframe>`;
		} else {
			contentHtml = `<a class="btn" href="${url}" target="_blank" rel="noopener">Abrir comprobante</a>`;
		}
	modalContent.innerHTML = contentHtml;
	// Use CSS class to show modal (matches .modal-overlay.active rules)
	modal.classList.add('active');
	btnCerrarModal && (btnCerrarModal.onclick = () => { modal.classList.remove('active'); URL.revokeObjectURL(url); });
	modal.onclick = (e) => { if (e.target === modal) { modal.classList.remove('active'); URL.revokeObjectURL(url); } };
	} catch (e) {
		alert('Error de conexión al cargar comprobante');
	}
}

// Editar pago
window.editarPago = async function(idPago) {
	try {
		const res = await authFetch(`/pagos/${idPago}`);
		const pago = await res.json();
		if (!res.ok) throw new Error(pago?.error || 'Error al obtener datos del pago');
		selectCliente.value = pago.id_cliente;
		await loadPaymentInfo();
			await loadPagosResumen();
		document.getElementById('monto_pagado').value = pago.monto_pagado;
		show(formSection);
		document.querySelector('#formPago button[type="submit"]').textContent = 'Actualizar Pago';
		formPago.dataset.editMode = 'true';
		formPago.dataset.editId = idPago;
	} catch (e) {
		alert('Error al cargar datos del pago: ' + e.message);
	}
}

// Eliminar pago
window.eliminarPago = async function(idPago) {
	if (!confirm('¿Estás seguro de que deseas eliminar este pago?')) return;
	try {
		const res = await authFetch(`/pagos/${idPago}`, { method: 'DELETE' });
		const data = await safeJson(res);
		if (!res.ok) throw new Error(data?.error || 'Error al eliminar pago');
		alert('Pago eliminado exitosamente');
			await loadPagosResumen();
		await loadPagos(currentPage, searchInput?.value || '');
	} catch (e) {
		alert('Error: ' + e.message);
	}
}

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
	// Elementos
	formSection = document.getElementById('formSection');
	formPago = document.getElementById('formPago');
	btnNuevoPago = document.getElementById('btnNuevoPago');
	btnCancelar = document.getElementById('btnCancelar');
	selectCliente = document.getElementById('id_cliente');
	btnCargarInfo = document.getElementById('btnCargarInfo');
	paymentInfo = document.getElementById('paymentInfo');
	montoPagadoInput = document.getElementById('monto_pagado');
	quedaraDebiendoInput = document.getElementById('quedara_debiendo');
	searchInput = document.getElementById('q');
	filtroClienteInput = document.getElementById('filtroCliente');
	btnBuscar = document.getElementById('btnBuscar');
	btnLimpiar = document.getElementById('btnLimpiar');
	tableBody = document.getElementById('rows');
	prevBtn = document.getElementById('prev');
	nextBtn = document.getElementById('next');
	pageInfo = document.getElementById('pageInfo');
	msg = document.getElementById('msg');

	// Auth guard
	if (!getToken()) { window.location.href = 'index.html'; return; }
	const ok = await validateToken();
	if (!ok) { window.location.href = 'index.html'; return; }
	const btnSalir = document.getElementById('btnSalir') || document.getElementById('logoutButton');
	if (btnSalir) btnSalir.onclick = (e) => { e.preventDefault(); setToken(null); logoutAPI(); };

	// Eventos UI
	if (btnNuevoPago) btnNuevoPago.onclick = () => show(formSection);
	if (btnCancelar) btnCancelar.onclick = () => { hide(formSection); formPago?.reset(); hide(paymentInfo); currentPaymentInfo = null; };
	if (btnCargarInfo) btnCargarInfo.onclick = loadPaymentInfo;
	if (btnBuscar) btnBuscar.onclick = () => { currentPage = 1; loadPagos(currentPage, searchInput?.value || ''); };
	if (btnLimpiar) btnLimpiar.onclick = () => { if (searchInput) searchInput.value = ''; if (filtroClienteInput) filtroClienteInput.value = ''; currentPage = 1; loadPagos(currentPage, ''); };
	if (prevBtn) prevBtn.onclick = () => { if (currentPage > 1) { currentPage--; loadPagos(currentPage, searchInput?.value || ''); } };
	if (nextBtn) nextBtn.onclick = () => { if (currentPage < totalPages) { currentPage++; loadPagos(currentPage, searchInput?.value || ''); } };
	if (montoPagadoInput) montoPagadoInput.addEventListener('input', () => {
		if (!currentPaymentInfo) return;
		const montoPagar = parseFloat(montoPagadoInput.value) || 0;
		const pendiente = Number(currentPaymentInfo.pago_info.monto_pendiente) || 0;
		const quedara = Math.max(0, pendiente - montoPagar);
		if (quedaraDebiendoInput) quedaraDebiendoInput.value = `S/ ${quedara.toFixed(2)}`;
	});
	if (formPago) formPago.addEventListener('submit', async (e) => {
		e.preventDefault();
		if (!currentPaymentInfo) { if (msg) msg.textContent = 'Primero debes cargar la información del cliente'; return; }
		const isEdit = formPago.dataset.editMode === 'true';
		const editId = formPago.dataset.editId;
		const formData = new FormData();
		formData.append('id_cliente', selectCliente?.value || '');
		formData.append('id_membresia', currentPaymentInfo?.membresia?.id_membresia || '');
		formData.append('monto_pagado', montoPagadoInput?.value || '');
		const comp = document.getElementById('comprobante')?.files?.[0];
		if (comp) formData.append('comprobante', comp);
		try {
			if (msg) msg.textContent = isEdit ? 'Actualizando pago...' : 'Registrando pago...';
			const url = isEdit ? `/pagos/${editId}` : '/pagos/';
			const method = isEdit ? 'PUT' : 'POST';
			const res = await authFetch(url, { method, body: formData });
			const data = await safeJson(res);
			if (!res.ok) throw new Error(data?.error || 'Error al guardar pago');
			if (msg) msg.textContent = isEdit ? 'Pago actualizado exitosamente' : 'Pago registrado exitosamente';
			hide(formSection); formPago.reset(); hide(paymentInfo); currentPaymentInfo = null;
			delete formPago.dataset.editMode; delete formPago.dataset.editId;
			const btnSubmit = document.querySelector('#formPago button[type="submit"]');
			if (btnSubmit) btnSubmit.textContent = 'Registrar Pago';
			await loadPagos(currentPage, searchInput?.value || '');
		} catch (e) {
			if (msg) msg.textContent = 'Error: ' + e.message;
		}
	});
	if (searchInput) searchInput.addEventListener('input', () => {
		clearTimeout(searchInput.debounceTimer);
		searchInput.debounceTimer = setTimeout(() => loadPagos(1, searchInput.value || ''), 500);
	});

	// Cargas iniciales
	await loadClientes();
	await loadPagosResumen();
	await loadPagos(1, '');
});

