const today = () => new Date().toISOString().slice(0, 10);
const currentMonth = () => new Date().toISOString().slice(0, 7);

function formatMoney(n) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
  }).format(n);
}

function showToast(msg, isError = false) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.toggle("error", isError);
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 3000);
}

// Tabs
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`panel-${tab.dataset.tab}`).classList.add("active");
  });
});

// Fecha por defecto
document.querySelectorAll('input[name="fecha"]').forEach((inp) => {
  inp.value = today();
});

// Selector de mes para PDF (mes actual por defecto)
document.querySelectorAll(".pdf-mes").forEach((inp) => {
  inp.value = currentMonth();
});

document.querySelectorAll(".btn-download-pdf").forEach((btn) => {
  btn.addEventListener("click", () => {
    const controls = btn.closest(".pdf-controls");
    const empresa = controls.dataset.empresa;
    const mesVal = controls.querySelector(".pdf-mes").value;
    if (!mesVal) {
      showToast("Seleccione un mes para el reporte", true);
      return;
    }
    const [anio, mes] = mesVal.split("-");
    window.open(`/api/pdf/${empresa}?anio=${anio}&mes=${parseInt(mes, 10)}`, "_blank");
  });
});

// GPS forms
document.querySelectorAll(".form-gps").forEach((form) => {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const empresa = form.dataset.empresa;
    const fd = new FormData(form);
    const body = Object.fromEntries(fd.entries());
    body.distancia = parseFloat(body.distancia);

    try {
      const res = await fetch(`/api/gps/${empresa}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Error al guardar");
      form.reset();
      form.querySelector('[name="fecha"]').value = today();
      showToast("Servicio registrado correctamente");
      loadGps(empresa);
    } catch (err) {
      showToast(err.message, true);
    }
  });
});

async function loadGps(empresa) {
  const res = await fetch(`/api/gps/${empresa}`);
  const rows = await res.json();
  const table = document.getElementById(`table-${empresa}`);
  const tbody = table.querySelector("tbody");
  const empty = table.closest(".table-wrap").querySelector(".empty-msg");

  tbody.innerHTML = "";
  if (!rows.length) {
    empty.classList.remove("hidden");
    table.classList.add("hidden");
    return;
  }
  empty.classList.add("hidden");
  table.classList.remove("hidden");

  rows.forEach((r) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.fecha}</td>
      <td><strong>${escapeHtml(r.codigo)}</strong></td>
      <td>${escapeHtml(r.ubicacion)}</td>
      <td>${Number(r.distancia).toFixed(1)}</td>
      <td>${escapeHtml(r.marca)}</td>
      <td>${escapeHtml(r.modelo)}</td>
      <td>${escapeHtml(r.patente)}</td>
      <td><button class="btn-delete" data-id="${r.id}" data-empresa="${empresa}">Eliminar</button></td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll(".btn-delete").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm("¿Eliminar este registro?")) return;
      const res = await fetch(`/api/gps/${btn.dataset.empresa}/${btn.dataset.id}`, {
        method: "DELETE",
      });
      if (res.ok) {
        showToast("Registro eliminado");
        loadGps(btn.dataset.empresa);
      }
    });
  });
}

// Egaña — ganancia preview
const formEgana = document.getElementById("form-egana");
const previewGanancia = document.getElementById("ganancia-preview");

function updateGananciaPreview() {
  const ins = parseFloat(formEgana.valor_insumos.value) || 0;
  const cob = parseFloat(formEgana.cobro_servicio.value) || 0;
  previewGanancia.textContent = formatMoney(cob - ins);
}

formEgana.valor_insumos.addEventListener("input", updateGananciaPreview);
formEgana.cobro_servicio.addEventListener("input", updateGananciaPreview);

formEgana.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(formEgana);
  const body = Object.fromEntries(fd.entries());
  body.valor_insumos = parseFloat(body.valor_insumos);
  body.cobro_servicio = parseFloat(body.cobro_servicio);

  try {
    const res = await fetch("/api/llaves", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al guardar");
    formEgana.reset();
    formEgana.fecha.value = today();
    updateGananciaPreview();
    showToast(`Servicio registrado. Ganancia: ${formatMoney(data.ganancia)}`);
    loadLlaves();
  } catch (err) {
    showToast(err.message, true);
  }
});

async function loadLlaves() {
  const res = await fetch("/api/llaves");
  const rows = await res.json();
  const table = document.getElementById("table-egana");
  const tbody = table.querySelector("tbody");
  const empty = table.closest(".table-wrap").querySelector(".empty-msg");

  let sumInsumos = 0;
  let sumCobro = 0;
  let sumGanancia = 0;

  tbody.innerHTML = "";
  if (!rows.length) {
    empty.classList.remove("hidden");
    table.classList.add("hidden");
  } else {
    empty.classList.add("hidden");
    table.classList.remove("hidden");

    rows.forEach((r) => {
      const g = r.ganancia ?? r.cobro_servicio - r.valor_insumos;
      sumInsumos += r.valor_insumos;
      sumCobro += r.cobro_servicio;
      sumGanancia += g;
      const cls = g >= 0 ? "ganancia-pos" : "ganancia-neg";
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${r.fecha}</td>
        <td>${escapeHtml(r.marca)}</td>
        <td>${escapeHtml(r.modelo)}</td>
        <td>${escapeHtml(r.patente)}</td>
        <td>${formatMoney(r.valor_insumos)}</td>
        <td>${formatMoney(r.cobro_servicio)}</td>
        <td class="${cls}">${formatMoney(g)}</td>
        <td><button class="btn-delete" data-id="${r.id}">Eliminar</button></td>
      `;
      tbody.appendChild(tr);
    });

    tbody.querySelectorAll(".btn-delete").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm("¿Eliminar este registro?")) return;
        const res = await fetch(`/api/llaves/${btn.dataset.id}`, { method: "DELETE" });
        if (res.ok) {
          showToast("Registro eliminado");
          loadLlaves();
        }
      });
    });
  }

  document.getElementById("sum-insumos").textContent = formatMoney(sumInsumos);
  document.getElementById("sum-cobro").textContent = formatMoney(sumCobro);
  document.getElementById("sum-ganancia").textContent = formatMoney(sumGanancia);
}

function escapeHtml(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

// Carga inicial
loadGps("mavi");
loadGps("tei");
loadLlaves();
updateGananciaPreview();
