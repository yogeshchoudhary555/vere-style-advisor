/* VÉRÉ Style Advisor — frontend flow */
const $ = (id) => document.getElementById(id);
let profile = null;

async function api(path, opts) {
  const r = await fetch(path, opts);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || `Request failed (${r.status})`);
  return data;
}

async function boot() {
  const s = await api("/api/status");
  const badge = $("modeBadge");
  badge.textContent = s.mode === "live" ? "LIVE · YouCam API" : "DEMO MODE · no API key";
  $("estNote").textContent = s.estimated_costs
    ? "(costs are documented estimates — set YOUCAM_API_KEY for live billing)"
    : "(live costs from your YouCam account)";
  refreshBudget();
}

function refreshBudget() {
  api("/api/budget").then((b) => {
    const tb = document.querySelector("#budgetTable tbody");
    tb.innerHTML = "";
    b.lines.forEach((l) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${l.n}. ${l.action}${l.detail ? " — " + l.detail : ""}
        ${l.estimated ? '<span class="est">(est.)</span>' : ""}</td>
        <td class="units">${l.units} units</td>`;
      tb.appendChild(tr);
    });
    $("budgetTotal").textContent = b.total_units + " units";
  }).catch(() => {});
}

function showProfile(p) {
  const box = $("profileBox");
  box.classList.remove("hidden");
  const chips = [
    ["Skin tone", p.skin_color], ["Eyes", p.eye_color], ["Lips", p.lip_color],
    ["Brows", p.eyebrow_color], ["Hair", p.hair_color],
  ];
  box.innerHTML = chips.map(([n, c]) =>
    `<div class="swatch"><span class="dot" style="background:${c}"></span>${n} · ${c}</div>`
  ).join("") + `<div class="tiny" style="width:100%">Profile source: ${p.source}</div>`;
}

async function analyze(file) {
  const fd = new FormData();
  fd.append("selfie", file);
  const data = await api("/api/analyze", { method: "POST", body: fd });
  profile = data.profile;
  showProfile(profile);
  loadVerdicts();
}

async function loadVerdicts() {
  const data = await api("/api/verdicts");
  $("step2").classList.remove("hidden");
  const grid = $("verdicts");
  grid.innerHTML = "";
  data.verdicts.forEach((v) => {
    const card = document.createElement("div");
    card.className = "item " + (v.keep ? "keep" : "refuse");
    card.innerHTML = `
      <div class="verdict">${v.keep ? "✓ Worth rendering" : "✕ Refused"}</div>
      <div class="score">${v.score}%</div>
      <div><b>${v.name}</b></div>
      <div class="reason">${v.reason}</div>
      ${v.keep ? `<button data-g="${v.garment_id}">Try it on</button>` : ""}`;
    grid.appendChild(card);
  });
  grid.querySelectorAll("button[data-g]").forEach((b) =>
    b.addEventListener("click", () => tryOn(b.dataset.g)));
}

async function tryOn(garmentId) {
  $("step3").classList.remove("hidden");
  $("tryonHint").textContent = "Rendering…";
  $("tryonResult").classList.add("hidden");
  const fd = new FormData();
  fd.append("garment_id", garmentId);
  try {
    const data = await api("/api/tryon", { method: "POST", body: fd });
    const img = $("tryonResult");
    img.src = data.image_url;
    img.classList.remove("hidden");
    $("tryonHint").textContent = "";
    $("tryonNote").textContent = data.note;
  } catch (e) {
    $("tryonHint").textContent = "Render failed: " + e.message;
  }
  refreshBudget();
  $("step3").scrollIntoView({ behavior: "smooth" });
}

$("analyzeBtn").addEventListener("click", async () => {
  const f = $("selfieInput").files[0];
  if (!f) { alert("Pick a selfie first (or use the demo portrait)."); return; }
  $("selfiePreview").src = URL.createObjectURL(f);
  $("selfiePreview").classList.remove("hidden");
  try { await analyze(f); } catch (e) { alert(e.message); }
});

$("useDemoBtn").addEventListener("click", async () => {
  const r = await fetch("/static/assets/demo_portrait.png");
  const blob = await r.blob();
  const file = new File([blob], "demo_portrait.png", { type: "image/png" });
  $("selfiePreview").src = URL.createObjectURL(blob);
  $("selfiePreview").classList.remove("hidden");
  try { await analyze(file); } catch (e) { alert(e.message); }
});

$("creditsBtn").addEventListener("click", async () => {
  try {
    const c = await api("/api/credits");
    $("creditsOut").textContent = `Spendable: ${c.api_spendable_units} units`;
  } catch (e) { $("creditsOut").textContent = e.message; }
});

boot();
