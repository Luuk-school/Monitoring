// Poll /latest_sysdata and render a card per host
const statusEl = document.getElementById('status');
const hostsContainer = document.getElementById('hosts');
const filterInput = document.getElementById('filter');
const refreshBtn = document.getElementById('refreshBtn');
const autoPollCheckbox = document.getElementById('autoPoll');

let polling = true;
let pollInterval = 2000;
let pollTimer = null;

function humanBytes(bytes) {
	if (bytes === null || bytes === undefined) return '—';
	const units = ['B','KB','MB','GB','TB'];
	let i = 0;
	let n = Number(bytes) || 0;
	while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
	return (i === 0 ? n.toFixed(0) : n.toFixed(2)) + ' ' + units[i];
}

function createCard(record) {
	const card = document.createElement('section');
	card.className = 'card';

	const h = document.createElement('h2');
	h.textContent = record.hostname || '—';
	card.appendChild(h);

	const ts = document.createElement('div');
	ts.innerHTML = `<strong>Last seen:</strong> ${record.timestamp || '—'}`;
	card.appendChild(ts);

	const cpu = document.createElement('div');
	cpu.innerHTML = `<strong>CPU:</strong> ${record.cpu_percent !== undefined ? record.cpu_percent+'%' : '—'}`;
	card.appendChild(cpu);

	const mem = record.memory || {};
	const memWrap = document.createElement('div');
	memWrap.innerHTML = `
		<strong>Memory:</strong>
		<div class="sub">Total: ${humanBytes(mem.total)} &nbsp; Used: ${humanBytes(mem.used)} &nbsp; Avail: ${humanBytes(mem.available)} &nbsp; ${mem.percent !== undefined ? mem.percent+'%' : ''}</div>
	`;
	card.appendChild(memWrap);

	const disk = record.disk || {};
	const diskWrap = document.createElement('div');
	diskWrap.innerHTML = `
		<strong>Disk:</strong>
		<div class="sub">Total: ${humanBytes(disk.total)} &nbsp; Used: ${humanBytes(disk.used)} &nbsp; Avail: ${humanBytes(disk.available)} &nbsp; ${disk.percent !== undefined ? disk.percent+'%' : ''}</div>
	`;
	card.appendChild(diskWrap);

	return card;
}

function renderHosts(list) {
	hostsContainer.innerHTML = '';
	if (!Array.isArray(list) || list.length === 0) {
		statusEl.textContent = 'No hosts reporting yet';
		return;
	}
	statusEl.textContent = `Showing ${list.length} host${list.length>1?'s':''}`;

	// sort by hostname for stable order
	list.sort((a,b) => (a.hostname||'').localeCompare(b.hostname||''));

	for (const rec of list) {
		const card = createCard(rec);
		hostsContainer.appendChild(card);
	}
}

async function fetchLatest() {
	try {
		const res = await fetch('/latest_sysdata');
		if (!res.ok) {
			statusEl.textContent = 'Error fetching data';
			return;
		}
		const data = await res.json();
				renderHosts(data);
	} catch (e) {
		statusEl.textContent = 'Fetch error';
		console.error(e);
	}
}

// initial load and polling
function startPolling(){
	if(pollTimer) clearInterval(pollTimer);
	if(autoPollCheckbox && autoPollCheckbox.checked){
		pollTimer = setInterval(fetchLatest, pollInterval);
		polling = true;
	}
}

function stopPolling(){
	if(pollTimer) clearInterval(pollTimer);
	pollTimer = null;
	polling = false;
}

// wire controls
if(refreshBtn) refreshBtn.addEventListener('click', () => fetchLatest());
if(autoPollCheckbox) autoPollCheckbox.addEventListener('change', () => {
	if(autoPollCheckbox.checked) startPolling(); else stopPolling();
});
if(filterInput) filterInput.addEventListener('input', () => fetchLatest());

// start
fetchLatest();
startPolling();
