<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DEA Suite</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #F7F6F3;
  --surface:   #FFFFFF;
  --border:    #E4E2DC;
  --border-md: #CCCAC2;
  --text:      #1A1917;
  --muted:     #6B6962;
  --hint:      #9B9890;

  --blue-50:   #E6F1FB; --blue-100: #B5D4F4;
  --blue-400:  #378ADD; --blue-600: #185FA5; --blue-800: #0C447C;
  --green-50:  #EAF3DE; --green-100: #C0DD97;
  --green-400: #639922; --green-600: #3B6D11; --green-800: #27500A;
  --amber-50:  #FAEEDA; --amber-400: #BA7517; --amber-600: #854F0B;
  --teal-50:   #E1F5EE; --teal-400:  #1D9E75; --teal-600: #0F6E56;
  --coral-50:  #FAECE7; --coral-400: #D85A30; --coral-600: #993C1D;
  --red-50:    #FCEBEB; --red-400:   #E24B4A; --red-600: #A32D2D;

  --rad-sm: 6px; --rad-md: 10px; --rad-lg: 14px; --rad-xl: 18px;
  --font: 'DM Sans', system-ui, sans-serif;
  --font-mono: 'DM Mono', 'Courier New', monospace;
}

html, body { height: 100%; }
body { font-family: var(--font); background: var(--bg); color: var(--text); font-size: 14px; line-height: 1.5; }

/* ── LAYOUT ── */
.app { display: flex; flex-direction: column; min-height: 100vh; }
.topbar { background: var(--surface); border-bottom: 1px solid var(--border); padding: 0 2rem; height: 56px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 100; }
.topbar-brand { display: flex; align-items: center; gap: 10px; }
.brand-logo { width: 28px; height: 28px; background: var(--blue-600); border-radius: 7px; display: flex; align-items: center; justify-content: center; }
.brand-logo svg { width: 16px; height: 16px; fill: none; stroke: #fff; stroke-width: 2; }
.brand-name { font-size: 15px; font-weight: 600; letter-spacing: -.01em; }
.brand-ver { font-size: 11px; color: var(--muted); background: var(--bg); border: 1px solid var(--border); padding: 1px 7px; border-radius: 20px; margin-left: 4px; }
.topbar-right { display: flex; align-items: center; gap: 8px; }
.solver-indicator { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--muted); padding: 4px 10px; border: 1px solid var(--border); border-radius: 20px; background: var(--bg); }
.solver-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--hint); }
.solver-dot.ok { background: var(--green-400); }

.main { flex: 1; display: grid; grid-template-columns: 280px 1fr; max-width: 1200px; width: 100%; margin: 0 auto; padding: 2rem 1rem; gap: 1.5rem; }

/* ── SIDEBAR ── */
.sidebar { display: flex; flex-direction: column; gap: 1rem; }
.step-nav { background: var(--surface); border: 1px solid var(--border); border-radius: var(--rad-lg); overflow: hidden; }
.step-item { display: flex; align-items: flex-start; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background .15s; position: relative; }
.step-item:last-child { border-bottom: none; }
.step-item.active { background: var(--blue-50); }
.step-item.done { cursor: default; }
.step-item:hover:not(.done):not(.active) { background: var(--bg); }
.step-badge { width: 26px; height: 26px; border-radius: 50%; border: 1.5px solid var(--border-md); background: var(--surface); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: var(--muted); flex-shrink: 0; margin-top: 1px; transition: all .15s; }
.step-item.active .step-badge { background: var(--blue-600); border-color: var(--blue-600); color: #fff; }
.step-item.done .step-badge { background: var(--green-600); border-color: var(--green-600); color: #fff; }
.step-text { flex: 1; }
.step-title { font-size: 13px; font-weight: 500; margin-bottom: 2px; }
.step-item.active .step-title { color: var(--blue-800); }
.step-item.done .step-title { color: var(--green-800); }
.step-desc { font-size: 11px; color: var(--muted); line-height: 1.4; }
.step-connector { position: absolute; left: 28px; top: 40px; bottom: -1px; width: 1px; background: var(--border); }
.step-item:last-child .step-connector { display: none; }

.info-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--rad-lg); padding: 1rem; }
.info-title { font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; margin-bottom: 10px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 12px; }
.info-row:last-child { border-bottom: none; padding-bottom: 0; }
.info-label { color: var(--muted); }
.info-val { font-weight: 500; font-family: var(--font-mono); font-size: 11px; }
.info-val.blue { color: var(--blue-600); }
.info-val.green { color: var(--green-600); }
.info-val.empty { color: var(--hint); font-weight: 400; font-family: var(--font); }

/* ── CONTENT ── */
.content { display: flex; flex-direction: column; gap: 1rem; }
.panel { display: none; }
.panel.active { display: flex; flex-direction: column; gap: 1.25rem; animation: slideIn .2s ease; }
@keyframes slideIn { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--rad-lg); }
.card-header { padding: 1rem 1.25rem; border-bottom: 1px solid var(--border); }
.card-title { font-size: 15px; font-weight: 600; margin-bottom: 2px; }
.card-sub { font-size: 12px; color: var(--muted); }
.card-body { padding: 1.25rem; }

/* ── UPLOAD ── */
.upload-zone { border: 1.5px dashed var(--border-md); border-radius: var(--rad-md); padding: 2.5rem 1.5rem; text-align: center; cursor: pointer; transition: all .2s; background: var(--bg); }
.upload-zone:hover, .upload-zone.drag { border-color: var(--blue-400); background: var(--blue-50); }
.upload-icon { font-size: 36px; margin-bottom: .75rem; display: block; }
.upload-title { font-size: 15px; font-weight: 500; margin-bottom: 4px; }
.upload-sub { font-size: 12px; color: var(--muted); }
.fmt-row { display: flex; gap: 6px; justify-content: center; margin-top: 12px; }
.fmt { font-size: 11px; padding: 2px 9px; border: 1px solid var(--border); border-radius: 20px; color: var(--muted); background: var(--surface); }

.file-banner { display: none; align-items: center; gap: 12px; padding: .875rem 1rem; background: var(--green-50); border: 1px solid var(--green-100); border-radius: var(--rad-md); }
.file-icon { font-size: 22px; }
.file-details { flex: 1; }
.file-name { font-size: 13px; font-weight: 500; color: var(--green-800); }
.file-meta { font-size: 11px; color: var(--teal-600); margin-top: 2px; }
.btn-xs { font-size: 11px; padding: 4px 10px; border-radius: var(--rad-sm); border: 1px solid var(--border); background: var(--surface); color: var(--muted); cursor: pointer; }
.btn-xs:hover { background: var(--bg); }

.preview-wrap { margin-top: 1rem; }
.preview-lbl { font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; margin-bottom: 6px; }
.tbl-scroll { overflow-x: auto; border: 1px solid var(--border); border-radius: var(--rad-md); }
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table th { background: var(--bg); padding: 7px 12px; text-align: left; font-weight: 600; border-bottom: 1px solid var(--border); color: var(--muted); white-space: nowrap; font-size: 11px; }
.data-table td { padding: 6px 12px; border-bottom: 1px solid var(--border); white-space: nowrap; font-family: var(--font-mono); font-size: 11px; }
.data-table tr:last-child td { border-bottom: none; }

/* ── COLUMN CLASSIFIER ── */
.col-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px,1fr)); gap: 8px; }
.col-card { border: 1.5px solid var(--border); border-radius: var(--rad-md); padding: .75rem; background: var(--surface); transition: border-color .15s, background .15s; }
.col-card.r-name      { border-color: #888780; background: #F1EFE8; }
.col-card.r-input     { border-color: var(--blue-400); background: var(--blue-50); }
.col-card.r-output    { border-color: var(--green-400); background: var(--green-50); }
.col-card.r-condition { border-color: var(--amber-400); background: var(--amber-50); }
.col-card.r-ignore    { border-color: var(--border); background: var(--bg); opacity: .6; }
.col-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 6px; margin-bottom: 6px; }
.col-colname { font-size: 12px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 110px; }
.role-sel { font-size: 11px; padding: 2px 5px; border: 1px solid var(--border); border-radius: var(--rad-sm); background: var(--surface); color: var(--text); cursor: pointer; }
.col-sample { font-size: 10px; color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: var(--font-mono); }
.role-pill { display: inline-flex; align-items: center; gap: 4px; font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 20px; text-transform: uppercase; letter-spacing: .03em; margin-bottom: 5px; }
.pill-name      { background: #D3D1C7; color: #444441; }
.pill-input     { background: var(--blue-100); color: var(--blue-800); }
.pill-output    { background: var(--green-100); color: var(--green-800); }
.pill-condition { background: var(--amber-50); color: var(--amber-600); }
.pill-ignore    { background: var(--border); color: var(--muted); }

.tally-bar { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 1rem; }
.tally-chip { display: flex; align-items: center; gap: 6px; padding: 5px 12px; border: 1px solid var(--border); border-radius: 20px; font-size: 12px; background: var(--surface); }
.tally-dot { width: 8px; height: 8px; border-radius: 50%; }
.td-name { background: #888780; }
.td-input { background: var(--blue-400); }
.td-output { background: var(--green-400); }
.td-condition { background: var(--amber-400); }

/* ── STEP 3: MODELS ── */
.model-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; }
.model-card { border: 1.5px solid var(--border); border-radius: var(--rad-md); padding: 1rem; cursor: pointer; background: var(--surface); transition: all .15s; user-select: none; }
.model-card:hover { border-color: var(--blue-400); }
.model-card.on { border-color: var(--blue-600); background: var(--blue-50); }
.model-check { width: 18px; height: 18px; border: 1.5px solid var(--border-md); border-radius: 4px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; transition: all .15s; }
.model-card.on .model-check { background: var(--blue-600); border-color: var(--blue-600); }
.model-check svg { display: none; }
.model-card.on .model-check svg { display: block; }
.model-tag-line { font-size: 10px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; margin-bottom: 4px; }
.model-card.on .model-tag-line { color: var(--blue-600); }
.model-mname { font-size: 14px; font-weight: 600; margin-bottom: 3px; }
.model-detail { font-size: 11px; color: var(--muted); line-height: 1.4; }
.type-pill { display: inline-block; font-size: 10px; padding: 1px 7px; border-radius: 20px; background: var(--bg); color: var(--muted); border: 1px solid var(--border); margin-top: 6px; font-family: var(--font-mono); }
.model-card.on .type-pill { background: var(--blue-100); color: var(--blue-800); border-color: var(--blue-100); }

/* ── OUTPUT ── */
.out-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 8px; }
.out-card { border: 1.5px solid var(--border); border-radius: var(--rad-md); padding: .875rem; cursor: pointer; display: flex; gap: 10px; align-items: flex-start; background: var(--surface); transition: all .15s; user-select: none; }
.out-card:hover { border-color: var(--teal-400); }
.out-card.on { border-color: var(--teal-600); background: var(--teal-50); }
.out-chk { width: 16px; height: 16px; border: 1.5px solid var(--border-md); border-radius: 4px; flex-shrink: 0; margin-top: 2px; display: flex; align-items: center; justify-content: center; transition: all .15s; }
.out-card.on .out-chk { background: var(--teal-600); border-color: var(--teal-600); }
.out-chk svg { display: none; }
.out-card.on .out-chk svg { display: block; }
.out-name { font-size: 13px; font-weight: 500; margin-bottom: 2px; }
.out-desc { font-size: 11px; color: var(--muted); line-height: 1.4; }

/* ── SOLVER PILLS ── */
.solver-row { display: flex; gap: 8px; }
.solver-card { flex: 1; border: 1.5px solid var(--border); border-radius: var(--rad-md); padding: .75rem 1rem; cursor: pointer; background: var(--surface); transition: all .15s; }
.solver-card:hover { border-color: var(--coral-400); }
.solver-card.on { border-color: var(--coral-600); background: var(--coral-50); }
.solver-radio { width: 16px; height: 16px; border: 1.5px solid var(--border-md); border-radius: 50%; margin-bottom: 8px; display: flex; align-items: center; justify-content: center; transition: all .15s; }
.solver-card.on .solver-radio { border-color: var(--coral-600); }
.solver-radio::after { content:''; width:8px; height:8px; border-radius:50%; background:var(--coral-600); display:none; }
.solver-card.on .solver-radio::after { display:block; }
.solver-sname { font-size: 13px; font-weight: 500; margin-bottom: 2px; }
.solver-sdesc { font-size: 11px; color: var(--muted); }
.solver-badge { font-size: 10px; padding: 1px 7px; border-radius: 20px; border: 1px solid var(--border); background: var(--bg); color: var(--muted); display: inline-block; margin-top: 5px; font-family: var(--font-mono); }
.solver-card.on .solver-badge { background: var(--coral-50); border-color: var(--coral-400); color: var(--coral-600); }

/* ── CONFIG SUMMARY ── */
.cfg-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.cfg-block { border: 1px solid var(--border); border-radius: var(--rad-md); padding: .875rem; }
.cfg-label { font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; margin-bottom: 6px; }
.cfg-chips { display: flex; flex-wrap: wrap; gap: 5px; }
.chip { font-size: 11px; padding: 2px 9px; border-radius: 20px; }
.chip-b { background: var(--blue-50); color: var(--blue-800); }
.chip-g { background: var(--green-50); color: var(--green-800); }
.chip-t { background: var(--teal-50); color: var(--teal-600); }

/* ── ALERTS ── */
.alert { border-radius: var(--rad-md); padding: .75rem 1rem; font-size: 12px; display: none; align-items: flex-start; gap: 8px; border-left: 3px solid; }
.alert.show { display: flex; }
.alert-warn { background: var(--amber-50); border-color: var(--amber-600); color: var(--amber-600); }
.alert-ok   { background: var(--green-50); border-color: var(--green-600); color: var(--green-800); }
.alert-info { background: var(--blue-50); border-color: var(--blue-600); color: var(--blue-800); }

/* ── BUTTONS ── */
.btn-row { display: flex; justify-content: space-between; align-items: center; margin-top: .5rem; }
.btn-back { display: flex; align-items: center; gap: 6px; padding: .5rem 1rem; border: 1px solid var(--border); border-radius: var(--rad-md); background: var(--surface); font-size: 13px; cursor: pointer; color: var(--text); }
.btn-back:hover { background: var(--bg); }
.btn-primary { display: flex; align-items: center; gap: 6px; padding: .5rem 1.25rem; background: var(--blue-600); color: #fff; border: none; border-radius: var(--rad-md); font-size: 13px; font-weight: 500; cursor: pointer; font-family: var(--font); transition: background .15s; }
.btn-primary:hover { background: var(--blue-800); }
.btn-primary:disabled { background: var(--border-md); cursor: not-allowed; }
.btn-run { width: 100%; padding: .875rem; background: var(--blue-600); color: #fff; border: none; border-radius: var(--rad-md); font-size: 15px; font-weight: 600; cursor: pointer; font-family: var(--font); display: flex; align-items: center; justify-content: center; gap: 8px; transition: background .15s; letter-spacing: -.01em; }
.btn-run:hover { background: var(--blue-800); }
.btn-run:disabled { background: var(--border-md); cursor: not-allowed; }

/* ── SECTION DIVIDERS ── */
.section-sep { font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; padding-bottom: 6px; border-bottom: 1px solid var(--border); margin-bottom: 10px; }

/* ── RESULT PANEL ── */
.result-panel { background: #0F1117; border-radius: var(--rad-lg); padding: 1.5rem; font-family: var(--font-mono); font-size: 12.5px; line-height: 1.8; color: #C9D1D9; }
.rp-comment { color: #6E7681; }
.rp-kw  { color: #FF7B72; }
.rp-str { color: #A5D6FF; }
.rp-num { color: #79C0FF; }
.rp-fn  { color: #D2A8FF; }
.rp-var { color: #FFA657; }
.rp-val { color: #56D364; }
.result-actions { display: flex; gap: 8px; margin-top: 1rem; }
.btn-copy { display: flex; align-items: center; gap: 6px; padding: .5rem 1rem; border: 1px solid #30363D; border-radius: var(--rad-md); background: #161B22; color: #C9D1D9; font-size: 12px; cursor: pointer; font-family: var(--font); }
.btn-copy:hover { background: #21262D; }
.btn-dl { display: flex; align-items: center; gap: 6px; padding: .5rem 1rem; background: var(--green-600); color: #fff; border: none; border-radius: var(--rad-md); font-size: 12px; cursor: pointer; font-family: var(--font); }
.btn-dl:hover { background: var(--green-800); }

/* ── MANUAL INPUT ── */
.manual-box { background: var(--bg); border: 1px solid var(--border); border-radius: var(--rad-md); padding: 1rem; }
.manual-box label { font-size: 12px; font-weight: 500; display: block; margin-bottom: 5px; color: var(--muted); }
.manual-box input { width: 100%; padding: .5rem .75rem; border: 1px solid var(--border); border-radius: var(--rad-sm); background: var(--surface); font-size: 13px; font-family: var(--font); color: var(--text); margin-bottom: .75rem; }
.manual-box input:focus { outline: none; border-color: var(--blue-400); }

@media (max-width: 700px) {
  .main { grid-template-columns: 1fr; }
  .sidebar { display: none; }
  .model-grid { grid-template-columns: 1fr; }
  .out-grid { grid-template-columns: 1fr; }
}
</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
</head>
<body>
<div class="app">

<!-- TOPBAR -->
<header class="topbar">
  <div class="topbar-brand">
    <div class="brand-logo">
      <svg viewBox="0 0 16 16"><polyline points="2,12 6,6 10,9 14,3"/><circle cx="14" cy="3" r="1.5" fill="white" stroke="none"/></svg>
    </div>
    <span class="brand-name">DEA Suite</span>
    <span class="brand-ver">v1.0.0</span>
  </div>
  <div class="topbar-right">
    <div class="solver-indicator">
      <div class="solver-dot" id="solver-dot"></div>
      <span id="solver-status-text">Verificando solver...</span>
    </div>
  </div>
</header>

<div class="main">

  <!-- SIDEBAR -->
  <aside class="sidebar">
    <nav class="step-nav">
      <div class="step-item active" id="snav-1" onclick="tryGoTo(1)">
        <div class="step-badge" id="sbadge-1">1</div>
        <div class="step-text">
          <div class="step-title">Cargar datos</div>
          <div class="step-desc">Excel (.xlsx) o CSV</div>
        </div>
        <div class="step-connector"></div>
      </div>
      <div class="step-item" id="snav-2">
        <div class="step-badge" id="sbadge-2">2</div>
        <div class="step-text">
          <div class="step-title">Clasificar variables</div>
          <div class="step-desc">Inputs, outputs y roles</div>
        </div>
        <div class="step-connector"></div>
      </div>
      <div class="step-item" id="snav-3">
        <div class="step-badge" id="sbadge-3">3</div>
        <div class="step-text">
          <div class="step-title">Modelos y salida</div>
          <div class="step-desc">MRM · DMESM · DMISM</div>
        </div>
        <div class="step-connector"></div>
      </div>
      <div class="step-item" id="snav-4">
        <div class="step-badge" id="sbadge-4">4</div>
        <div class="step-text">
          <div class="step-title">Ejecutar</div>
          <div class="step-desc">Script generado</div>
        </div>
      </div>
    </nav>

    <!-- Live config summary -->
    <div class="info-card">
      <div class="info-title">Configuración actual</div>
      <div class="info-row"><span class="info-label">Archivo</span><span class="info-val blue" id="si-file">—</span></div>
      <div class="info-row"><span class="info-label">Inputs</span><span class="info-val blue" id="si-inputs">—</span></div>
      <div class="info-row"><span class="info-label">Outputs</span><span class="info-val green" id="si-outputs">—</span></div>
      <div class="info-row"><span class="info-label">Modelos</span><span class="info-val" id="si-models">—</span></div>
      <div class="info-row"><span class="info-label">Solver</span><span class="info-val" id="si-solver">SCIP</span></div>
      <div class="info-row"><span class="info-label">Salida</span><span class="info-val" id="si-output">Excel</span></div>
    </div>
  </aside>

  <!-- CONTENT -->
  <main class="content">

    <!-- ── PASO 1 ── -->
    <div class="panel active" id="panel-1">
      <div class="card">
        <div class="card-header">
          <div class="card-title">Cargar dataset</div>
          <div class="card-sub">Seleccioná un archivo con los datos de las DMUs. Filas = unidades, columnas = variables.</div>
        </div>
        <div class="card-body">
          <input type="file" id="file-input" accept=".xlsx,.csv,.xls" style="display:none">
          <div class="upload-zone" id="upload-zone">
            <span class="upload-icon">📂</span>
            <div class="upload-title">Arrastrá el archivo o hacé clic para seleccionar</div>
            <div class="upload-sub">Primera fila = encabezados de columna</div>
            <div class="fmt-row">
              <span class="fmt">.xlsx</span><span class="fmt">.xls</span><span class="fmt">.csv</span>
            </div>
          </div>
          <div class="file-banner" id="file-banner">
            <span class="file-icon">📊</span>
            <div class="file-details">
              <div class="file-name" id="file-name-txt">—</div>
              <div class="file-meta" id="file-meta-txt">—</div>
            </div>
            <button class="btn-xs" id="file-clear-btn">Cambiar</button>
          </div>
          <div id="preview-wrap" class="preview-wrap" style="display:none">
            <div class="preview-lbl">Vista previa — primeras 5 filas</div>
            <div class="tbl-scroll"><table class="data-table" id="preview-tbl"></table></div>
          </div>
          <div class="alert alert-warn" id="alert-1"><span id="alert-1-msg"></span></div>
        </div>
      </div>
      <div class="btn-row">
        <span></span>
        <button class="btn-primary" id="next-1" disabled>Siguiente →</button>
      </div>
    </div>

    <!-- ── PASO 2 ── -->
    <div class="panel" id="panel-2">
      <div class="card">
        <div class="card-header">
          <div class="card-title">Clasificar variables</div>
          <div class="card-sub">Asigná el rol de cada columna. Se necesita exactamente 1 nombre DMU, ≥1 input, ≥1 output y 1 columna Condition.</div>
        </div>
        <div class="card-body">
          <div id="manual-input-box" class="manual-box" style="display:none">
            <label>Nombres de columnas (separados por coma)</label>
            <input id="manual-cols-input" placeholder="Ej: Empresa, Empleados, Combustible, Pasajeros, Carga, Condition">
            <button class="btn-primary" onclick="applyManualCols()" style="font-size:12px;padding:.4rem .9rem">Aplicar columnas</button>
          </div>
          <div id="col-grid" class="col-grid"></div>
          <div class="tally-bar" id="tally-bar"></div>
          <div class="alert alert-warn" id="alert-2"><span id="alert-2-msg"></span></div>
        </div>
      </div>
      <div class="btn-row">
        <button class="btn-back" onclick="goTo(1)">← Atrás</button>
        <button class="btn-primary" id="next-2" disabled>Siguiente →</button>
      </div>
    </div>

    <!-- ── PASO 3 ── -->
    <div class="panel" id="panel-3">
      <div class="card">
        <div class="card-header">
          <div class="card-title">Modelos y formato de salida</div>
          <div class="card-sub">Elegí qué modelos ejecutar, el formato del reporte y el solver de optimización.</div>
        </div>
        <div class="card-body" style="display:flex;flex-direction:column;gap:1.5rem">

          <div>
            <div class="section-sep">Modelos DEA</div>
            <div class="model-grid">
              <div class="model-card on" id="mc-mrm" onclick="toggleModel('mrm')">
                <div class="model-check"><svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4L4 7L9 1" stroke="white" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                <div class="model-tag-line">Modelo 1</div>
                <div class="model-mname">MRM</div>
                <div class="model-detail">Maximiza el movimiento equi-proporcional mínimo hacia la frontera.</div>
                <div class="type-pill">LP + SOS1</div>
              </div>
              <div class="model-card on" id="mc-dmesm" onclick="toggleModel('dmesm')">
                <div class="model-check"><svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4L4 7L9 1" stroke="white" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                <div class="model-tag-line">Modelo 2</div>
                <div class="model-mname">DMESM</div>
                <div class="model-detail">Minimiza la varianza de las distancias relativas de proyección.</div>
                <div class="type-pill">QP + SOS1</div>
              </div>
              <div class="model-card on" id="mc-dmism" onclick="toggleModel('dmism')">
                <div class="model-check"><svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4L4 7L9 1" stroke="white" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                <div class="model-tag-line">Modelo 3</div>
                <div class="model-mname">DMISM</div>
                <div class="model-detail">Minimiza la desviación respecto al slack relativo mínimo.</div>
                <div class="type-pill">QP + SOS1 + bin</div>
              </div>
            </div>
          </div>

          <div>
            <div class="section-sep">Formato de salida</div>
            <div class="out-grid">
              <div class="out-card on" id="oc-excel" onclick="toggleOut('excel')">
                <div class="out-chk"><svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4L4 7L9 1" stroke="white" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                <div><div class="out-name">Excel (.xlsx)</div><div class="out-desc">Una hoja por modelo con todos los resultados</div></div>
              </div>
              <div class="out-card" id="oc-csv" onclick="toggleOut('csv')">
                <div class="out-chk"><svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4L4 7L9 1" stroke="white" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                <div><div class="out-name">CSV por modelo</div><div class="out-desc">Archivo .csv separado para cada modelo</div></div>
              </div>
              <div class="out-card" id="oc-json" onclick="toggleOut('json')">
                <div class="out-chk"><svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4L4 7L9 1" stroke="white" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                <div><div class="out-name">JSON</div><div class="out-desc">Resultado estructurado completo de la solución</div></div>
              </div>
              <div class="out-card on" id="oc-console" onclick="toggleOut('console')">
                <div class="out-chk"><svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4L4 7L9 1" stroke="white" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                <div><div class="out-name">Consola</div><div class="out-desc">Imprime progreso en stdout durante la ejecución</div></div>
              </div>
            </div>
          </div>

          <div>
            <div class="section-sep">Solver de optimización</div>
            <div class="solver-row">
              <div class="solver-card on" id="sc-scip" onclick="selectSolver('scip')">
                <div class="solver-radio"></div>
                <div class="solver-sname">SCIP</div>
                <div class="solver-sdesc">Open-source, sin licencia</div>
                <div class="solver-badge">pyscipopt</div>
              </div>
              <div class="solver-card" id="sc-gurobi" onclick="selectSolver('gurobi')">
                <div class="solver-radio"></div>
                <div class="solver-sname">Gurobi</div>
                <div class="solver-sdesc">Más veloz, requiere licencia</div>
                <div class="solver-badge">gurobipy</div>
              </div>
              <div class="solver-card" id="sc-auto" onclick="selectSolver('auto')">
                <div class="solver-radio"></div>
                <div class="solver-sname">Automático</div>
                <div class="solver-sdesc">Primer solver disponible</div>
                <div class="solver-badge">default</div>
              </div>
            </div>
          </div>

          <div id="dir-block">
            <div class="section-sep">Directorio de salida</div>
            <input id="out-dir" type="text" value="output/" placeholder="output/" style="width:100%;padding:.5rem .75rem;border:1px solid var(--border);border-radius:var(--rad-sm);font-size:13px;font-family:var(--font-mono);background:var(--surface);color:var(--text)">
            <div style="font-size:11px;color:var(--muted);margin-top:4px">Relativo al archivo de datos. Se crea automáticamente si no existe.</div>
          </div>

          <div class="alert alert-warn" id="alert-3"><span id="alert-3-msg"></span></div>
        </div>
      </div>
      <div class="btn-row">
        <button class="btn-back" onclick="goTo(2)">← Atrás</button>
        <button class="btn-primary" id="next-3" onclick="goTo(4); buildScript()">Generar script →</button>
      </div>
    </div>

    <!-- ── PASO 4 ── -->
    <div class="panel" id="panel-4">
      <div class="card">
        <div class="card-header">
          <div class="card-title">Script generado</div>
          <div class="card-sub">Guardá este archivo como <code style="font-family:var(--font-mono);font-size:12px;background:var(--bg);padding:1px 6px;border-radius:4px">run_analysis.py</code> en la carpeta del dataset y ejecutalo con <code style="font-family:var(--font-mono);font-size:12px;background:var(--bg);padding:1px 6px;border-radius:4px">python run_analysis.py</code></div>
        </div>
        <div class="card-body">
          <div class="result-panel" id="script-output"></div>
          <div class="result-actions">
            <button class="btn-copy" id="copy-btn" onclick="copyScript()">📋 Copiar</button>
            <button class="btn-dl" id="dl-btn" onclick="downloadScript()">⬇ Descargar run_analysis.py</button>
          </div>
        </div>
      </div>
      <div class="btn-row">
        <button class="btn-back" onclick="goTo(3)">← Editar configuración</button>
        <span style="font-size:12px;color:var(--muted)">Script listo ✓</span>
      </div>
    </div>

  </main>
</div>
</div>

<script>
var S = {
  fileName:'', headers:[], rows:[], colRoles:{},
  models:{mrm:true,dmesm:true,dmism:true},
  outputs:{excel:true,csv:false,json:false,console:true},
  solver:'scip', outDir:'output/', manualMode:false,
  step:1, generatedScript:''
};

// ── SOLVER STATUS ─────────────────────────────────────────────────────────────
function checkSolver(){
  fetch('/api/solvers').then(function(r){return r.json();}).then(function(d){
    var dot=document.getElementById('solver-dot');
    var txt=document.getElementById('solver-status-text');
    if(d.solvers&&d.solvers.length>0){
      dot.classList.add('ok');
      txt.textContent=d.solvers[0]+' disponible';
    } else {
      txt.textContent='Sin solver — instalar pyscipopt';
    }
  }).catch(function(){
    document.getElementById('solver-status-text').textContent='Servidor local activo';
    document.getElementById('solver-dot').classList.add('ok');
  });
}
checkSolver();

// ── NAVIGATION ────────────────────────────────────────────────────────────────
function goTo(n){
  S.step=n;
  for(var i=1;i<=4;i++){
    var p=document.getElementById('panel-'+i);
    var sn=document.getElementById('snav-'+i);
    var sb=document.getElementById('sbadge-'+i);
    p.classList.toggle('active',i===n);
    sn.classList.remove('active','done');
    sb.innerHTML=i;
    if(i<n){sn.classList.add('done');sb.innerHTML='✓';}
    else if(i===n){sn.classList.add('active');}
  }
  updateSidebar();
}
function tryGoTo(n){if(n<S.step)goTo(n);}

// ── FILE HANDLING ─────────────────────────────────────────────────────────────
var zone=document.getElementById('upload-zone');
var fi=document.getElementById('file-input');
zone.addEventListener('click',function(){fi.click();});
zone.addEventListener('dragover',function(e){e.preventDefault();zone.classList.add('drag');});
zone.addEventListener('dragleave',function(){zone.classList.remove('drag');});
zone.addEventListener('drop',function(e){e.preventDefault();zone.classList.remove('drag');if(e.dataTransfer.files[0])handleFile(e.dataTransfer.files[0]);});
fi.addEventListener('change',function(){if(fi.files[0])handleFile(fi.files[0]);});
document.getElementById('file-clear-btn').addEventListener('click',clearFile);

function clearFile(){
  S.file=null;S.fileName='';S.rows=[];S.headers=[];S.colRoles={};S.manualMode=false;
  document.getElementById('file-banner').style.display='none';
  zone.style.display='';
  document.getElementById('preview-wrap').style.display='none';
  document.getElementById('next-1').disabled=true;
  fi.value=''; hideAlert('alert-1'); updateSidebar();
}

function handleFile(f){
  S.fileName=f.name;
  var ext=f.name.split('.').pop().toLowerCase();
  if(ext==='csv'){
    readCSV(f);
  } else {
    // Excel: use API endpoint if available, else manual mode
    uploadFile(f);
  }
}

function uploadFile(f){
  var fd=new FormData(); fd.append('file',f);
  fetch('/api/upload',{method:'POST',body:fd}).then(function(r){return r.json();}).then(function(d){
    if(d.headers&&d.rows){
      S.headers=d.headers; S.rows=d.rows; S.manualMode=false;
      autoDetectRoles(d.headers,d.rows);
      renderPreview(d.headers,d.rows);
      showFileBanner(f.name,f.size,d.headers.length+' columnas, '+d.total_rows+' filas');
      document.getElementById('next-1').disabled=false;
      hideAlert('alert-1');
    }
  }).catch(function(){
    // Fallback: manual mode
    S.manualMode=true; S.headers=[]; S.rows=[];
    showFileBanner(f.name,f.size,'Definí las columnas manualmente en el paso 2');
    showAlert('alert-1','warn','Archivo Excel cargado. Definí las columnas en el paso 2 (o usá CSV para detección automática).');
    document.getElementById('next-1').disabled=false;
  });
  document.getElementById('si-file').textContent=f.name.length>18?f.name.slice(0,16)+'…':f.name;
}

function readCSV(f){
  var reader=new FileReader();
  reader.onload=function(e){
    var text=e.target.result;
    var lines=text.trim().split(/\r?\n/);
    if(lines.length<2){showAlert('alert-1','warn','El archivo parece vacío.');return;}
    var sep=detectSep(text);
    var headers=splitLine(lines[0],sep);
    var rows=lines.slice(1,6).map(function(l){return splitLine(l,sep);});
    S.headers=headers; S.rows=rows; S.manualMode=false;
    autoDetectRoles(headers,rows);
    renderPreview(headers,rows);
    showFileBanner(f.name,f.size,headers.length+' columnas · '+(lines.length-1)+' filas');
    document.getElementById('next-1').disabled=false;
    hideAlert('alert-1');
    document.getElementById('si-file').textContent=f.name.length>18?f.name.slice(0,16)+'…':f.name;
  };
  reader.readAsText(f);
}

function detectSep(t){
  var commas=(t.match(/,/g)||[]).length;
  var semis=(t.match(/;/g)||[]).length;
  return semis>commas?';':',';
}
function splitLine(l,sep){
  return l.split(sep).map(function(c){return c.replace(/^"|"$/g,'').trim();});
}
function showFileBanner(name,size,meta){
  document.getElementById('file-banner').style.display='flex';
  zone.style.display='none';
  document.getElementById('file-name-txt').textContent=name;
  document.getElementById('file-meta-txt').textContent=(size/1024).toFixed(1)+' KB — '+meta;
}
function renderPreview(headers,rows){
  var t=document.getElementById('preview-tbl');
  var th='<thead><tr>'+headers.map(function(h){return '<th>'+esc(h)+'</th>';}).join('')+'</tr></thead>';
  var tb='<tbody>'+rows.map(function(r){
    return '<tr>'+headers.map(function(h,i){return '<td>'+(r[i]!==undefined?esc(r[i]):'')+'</td>';}).join('')+'</tr>';
  }).join('')+'</tbody>';
  t.innerHTML=th+tb;
  document.getElementById('preview-wrap').style.display='block';
}

// ── STEP 2: CLASSIFIER ────────────────────────────────────────────────────────
document.getElementById('next-1').addEventListener('click',function(){goTo(2);renderClassifier();});
document.getElementById('next-2').addEventListener('click',function(){goTo(3);validateStep3();});

function autoDetectRoles(headers,rows){
  S.colRoles={};
  headers.forEach(function(h,i){
    var hl=h.toLowerCase();
    if(i===0){S.colRoles[h]='name';return;}
    if(hl==='condition'||hl==='condicion'||hl==='cond'){S.colRoles[h]='condition';return;}
    var numeric=rows.length>0&&rows.every(function(r){return r[i]!==undefined&&!isNaN(parseFloat(r[i]))&&r[i].trim()!=='';});
    if(numeric){
      var numericCols=headers.filter(function(hh,ii){return ii>0&&hh.toLowerCase()!=='condition'&&hh.toLowerCase()!=='condicion';});
      var ni=numericCols.indexOf(h);
      S.colRoles[h]=ni<Math.ceil(numericCols.length/2)?'input':'output';
    } else { S.colRoles[h]='ignore'; }
  });
}

function renderClassifier(){
  var grid=document.getElementById('col-grid');
  grid.innerHTML='';
  var mb=document.getElementById('manual-input-box');
  if(S.manualMode&&S.headers.length===0){
    mb.style.display='block'; updateTally(); validateStep2(); return;
  }
  mb.style.display='none';
  var headers=S.headers.length>0?S.headers:[];
  if(headers.length===0){mb.style.display='block';updateTally();validateStep2();return;}

  headers.forEach(function(h){
    var role=S.colRoles[h]||'ignore';
    var sample=S.rows.length>0?(S.rows[0][S.headers.indexOf(h)]||''):'-';
    var card=document.createElement('div');
    card.className='col-card r-'+role;
    card.dataset.col=h;
    var pillLabel={name:'Nombre',input:'Input',output:'Output',condition:'Condition',ignore:'Ignorar'}[role];
    card.innerHTML=
      '<div class="col-top">'+
        '<span class="col-colname" title="'+esc(h)+'">'+esc(h)+'</span>'+
        '<select class="role-sel" data-col="'+esc(h)+'">'+
          ['name','input','output','condition','ignore'].map(function(r){
            var labels={name:'Nombre DMU',input:'Input',output:'Output',condition:'Condition',ignore:'Ignorar'};
            return '<option value="'+r+'"'+(r===role?' selected':'')+'>'+labels[r]+'</option>';
          }).join('')+
        '</select>'+
      '</div>'+
      '<div class="role-pill pill-'+role+'">'+pillLabel+'</div>'+
      '<div class="col-sample">'+esc(String(sample).slice(0,25))+'</div>';
    grid.appendChild(card);
    card.querySelector('select').addEventListener('change',function(e){
      var col=e.target.getAttribute('data-col');
      var r=e.target.value;
      S.colRoles[col]=r;
      var c=document.querySelector('.col-card[data-col="'+col+'"]');
      c.className='col-card r-'+r;
      var pillLabel={name:'Nombre',input:'Input',output:'Output',condition:'Condition',ignore:'Ignorar'}[r];
      c.querySelector('.role-pill').className='role-pill pill-'+r;
      c.querySelector('.role-pill').textContent=pillLabel;
      updateTally(); validateStep2(); updateSidebar();
    });
  });
  updateTally(); validateStep2();
}

window.applyManualCols=function(){
  var val=document.getElementById('manual-cols-input').value.trim();
  if(!val)return;
  var cols=val.split(',').map(function(c){return c.trim();}).filter(Boolean);
  S.headers=cols; S.rows=[]; S.manualMode=false;
  autoDetectRoles(cols,[]);
  renderClassifier();
};

function updateTally(){
  var r=S.colRoles;
  var counts={name:0,input:0,output:0,condition:0};
  Object.values(r).forEach(function(v){if(counts[v]!==undefined)counts[v]++;});
  var bar=document.getElementById('tally-bar');
  bar.innerHTML=[
    {cls:'td-name',label:'Nombre',k:'name'},
    {cls:'td-input',label:'Inputs',k:'input'},
    {cls:'td-output',label:'Outputs',k:'output'},
    {cls:'td-condition',label:'Condition',k:'condition'},
  ].map(function(x){
    return '<div class="tally-chip"><div class="tally-dot '+x.cls+'"></div><strong>'+counts[x.k]+'</strong><span style="color:var(--muted)">'+x.label+'</span></div>';
  }).join('');
}

function validateStep2(){
  var r=S.colRoles;
  var errs=[];
  var inputs=Object.keys(r).filter(function(k){return r[k]==='input';});
  var outputs=Object.keys(r).filter(function(k){return r[k]==='output';});
  var names=Object.keys(r).filter(function(k){return r[k]==='name';});
  var conds=Object.keys(r).filter(function(k){return r[k]==='condition';});
  if(names.length!==1)errs.push('exactamente 1 columna de nombre DMU');
  if(inputs.length<1)errs.push('al menos 1 input');
  if(outputs.length<1)errs.push('al menos 1 output');
  if(conds.length!==1)errs.push('exactamente 1 columna Condition');
  var ok=errs.length===0;
  document.getElementById('next-2').disabled=!ok;
  if(!ok)showAlert('alert-2','warn','Faltan: '+errs.join(' · '));
  else hideAlert('alert-2');
  updateSidebar();
  return ok;
}

// ── STEP 3 ────────────────────────────────────────────────────────────────────
function toggleModel(m){
  S.models[m]=!S.models[m];
  document.getElementById('mc-'+m).classList.toggle('on',S.models[m]);
  validateStep3();
}
function toggleOut(o){
  S.outputs[o]=!S.outputs[o];
  document.getElementById('oc-'+o).classList.toggle('on',S.outputs[o]);
  validateStep3(); updateSidebar();
}
function selectSolver(s){
  S.solver=s;
  ['scip','gurobi','auto'].forEach(function(x){document.getElementById('sc-'+x).classList.toggle('on',x===s);});
  updateSidebar();
}
function validateStep3(){
  var anyModel=Object.values(S.models).some(Boolean);
  var anyOut=Object.values(S.outputs).some(Boolean);
  var ok=anyModel&&anyOut;
  document.getElementById('next-3').disabled=!ok;
  if(!anyModel)showAlert('alert-3','warn','Seleccioná al menos un modelo.');
  else if(!anyOut)showAlert('alert-3','warn','Seleccioná al menos un formato de salida.');
  else hideAlert('alert-3');
  updateSidebar();
}

// ── SIDEBAR SYNC ─────────────────────────────────────────────────────────────
function updateSidebar(){
  var r=S.colRoles;
  var inputs=Object.keys(r).filter(function(k){return r[k]==='input';});
  var outputs=Object.keys(r).filter(function(k){return r[k]==='output';});
  var mods=Object.keys(S.models).filter(function(k){return S.models[k];}).map(function(m){return m.toUpperCase();});
  var outs=Object.keys(S.outputs).filter(function(k){return S.outputs[k];});
  document.getElementById('si-file').textContent=S.fileName?(S.fileName.length>16?S.fileName.slice(0,14)+'…':S.fileName):'—';
  document.getElementById('si-file').className='info-val '+(S.fileName?'blue':'empty');
  document.getElementById('si-inputs').textContent=inputs.length>0?inputs.join(', '):'—';
  document.getElementById('si-inputs').className='info-val '+(inputs.length?'blue':'empty');
  document.getElementById('si-outputs').textContent=outputs.length>0?outputs.join(', '):'—';
  document.getElementById('si-outputs').className='info-val '+(outputs.length?'green':'empty');
  document.getElementById('si-models').textContent=mods.length?mods.join(' · '):'—';
  document.getElementById('si-solver').textContent=S.solver;
  document.getElementById('si-output').textContent=outs.length?outs.map(function(o){return o.charAt(0).toUpperCase()+o.slice(1);}).join(', '):'—';
}

// ── SCRIPT GENERATION ─────────────────────────────────────────────────────────
function buildScript(){
  var r=S.colRoles;
  var inputs=Object.keys(r).filter(function(k){return r[k]==='input';});
  var outputs=Object.keys(r).filter(function(k){return r[k]==='output';});
  var namecol=Object.keys(r).filter(function(k){return r[k]==='name';})[0]||'DMU';
  var condcol=Object.keys(r).filter(function(k){return r[k]==='condition';})[0]||'Condition';
  var models=Object.keys(S.models).filter(function(k){return S.models[k];});
  var solver=S.solver==='auto'?'None':"'"+S.solver+"'";
  var outdir=document.getElementById('out-dir').value.trim()||'output/';
  var fname=S.fileName||'datos.xlsx';

  var lines=[];
  lines.push('# -*- coding: utf-8 -*-');
  lines.push('"""');
  lines.push('Análisis DEA — generado por DEA Suite UI');
  lines.push('Dataset  : '+fname);
  lines.push('Modelos  : '+models.map(function(m){return m.toUpperCase();}).join(', '));
  lines.push('Solver   : '+S.solver);
  lines.push('"""');
  lines.push('');
  lines.push('import dea_suite as dea');
  lines.push('from pathlib import Path');
  lines.push('');
  lines.push('DATA_FILE  = Path(__file__).parent / "'+fname+'"');
  lines.push('OUTPUT_DIR = Path(__file__).parent / "'+outdir+'"');
  lines.push('SOLVER     = '+solver);
  lines.push('');
  lines.push('# ── Cargar dataset ──────────────────────────────────────────────');
  lines.push('print("Cargando dataset:", DATA_FILE.name)');
  lines.push('');
  lines.push('ds = dea.load_dataset(');
  lines.push('    filepath         = DATA_FILE,');
  lines.push('    n_inputs         = '+inputs.length+',  # '+inputs.join(', '));
  lines.push('    n_outputs        = '+outputs.length+',  # '+outputs.join(', '));
  if(condcol!=='Condition') lines.push('    condition_col    = "'+condcol+'",');
  lines.push(')');
  lines.push('');
  lines.push('print(f"  DMUs eficientes  : {ds.n_eff}")');
  lines.push('print(f"  DMUs ineficientes: {ds.n_ineff}")');
  lines.push('print(f"  Inputs           : {ds.inputs}")');
  lines.push('print(f"  Outputs          : {ds.outputs}")');
  lines.push('print()');
  lines.push('');
  lines.push('# ── Ejecutar modelos ────────────────────────────────────────────');
  lines.push('results = {}');
  lines.push('');

  models.forEach(function(m){
    var fname2=m.toUpperCase();
    lines.push('print("--- '+fname2+' ---")');
    lines.push('results["'+fname2+'"] = dea.run_'+m+'(ds, solver=SOLVER, verbose=True)');
    lines.push('print()');
    lines.push('');
  });

  lines.push('# ── Guardar resultados ──────────────────────────────────────────');

  if(S.outputs.excel){
    lines.push('excel_path = dea.save_report(');
    lines.push('    results       = results,');
    lines.push('    base_filename = "DEASuite_'+fname.replace(/\.[^.]+$/,'')+'",');
    lines.push('    output_dir    = OUTPUT_DIR,');
    lines.push(')');
    lines.push('print("Excel guardado:", excel_path)');
    lines.push('');
  }

  if(S.outputs.csv){
    lines.push('# CSV por modelo');
    lines.push('OUTPUT_DIR.mkdir(parents=True, exist_ok=True)');
    lines.push('for model_name, df in results.items():');
    lines.push('    csv_path = OUTPUT_DIR / f"DEASuite_{model_name}.csv"');
    lines.push('    df.to_csv(csv_path, index=False)');
    lines.push('    print(f"CSV guardado: {csv_path}")');
    lines.push('');
  }

  if(S.outputs.json){
    lines.push('# JSON completo');
    lines.push('import json, datetime');
    lines.push('json_out = {');
    lines.push('    "dataset": str(DATA_FILE),');
    lines.push('    "generated": datetime.datetime.now().isoformat(),');
    lines.push('    "inputs": ds.inputs,');
    lines.push('    "outputs": ds.outputs,');
    lines.push('    "models": {k: v.to_dict(orient="records") for k,v in results.items()},');
    lines.push('}');
    lines.push('json_path = OUTPUT_DIR / "DEASuite_results.json"');
    lines.push('OUTPUT_DIR.mkdir(parents=True, exist_ok=True)');
    lines.push('json_path.write_text(json.dumps(json_out, indent=2, ensure_ascii=False))');
    lines.push('print("JSON guardado:", json_path)');
    lines.push('');
  }

  if(S.outputs.console){
    lines.push('# Resumen en consola');
    lines.push('print()');
    lines.push('print("=" * 60)');
    lines.push('print("  Resumen de resultados")');
    lines.push('print("=" * 60)');
    lines.push('for model_name, df in results.items():');
    lines.push('    if "Obj Value" in df.columns:');
    lines.push('        print(f"\\n{model_name}:")');
    lines.push('        print(df[["Obj Value","Sum_Cambio"]].to_string())');
  }

  lines.push('');
  lines.push('print("\\nDone.")');

  S.generatedScript=lines.join('\n');
  renderScript(lines);
}

function renderScript(lines){
  var kw=['import','from','as','def','class','return','for','in','if','else','elif','True','False','None','print','with','pass'];
  var html=lines.map(function(line){
    if(line.startsWith('#')){return '<span class="rp-comment">'+esc(line)+'</span>';}
    if(line.startsWith('"""')||line==='"""'){return '<span class="rp-comment">'+esc(line)+'</span>';}
    var escaped=esc(line);
    kw.forEach(function(k){
      escaped=escaped.replace(new RegExp('\\b'+k+'\\b','g'),'<span class="rp-kw">'+k+'</span>');
    });
    escaped=escaped.replace(/"([^"]*)"/g,'"<span class="rp-str">$1</span>"');
    escaped=escaped.replace(/\b(\d+)\b/g,'<span class="rp-num">$1</span>');
    escaped=escaped.replace(/\b(dea\.\w+)\b/g,'<span class="rp-fn">$1</span>');
    return escaped;
  }).join('\n');
  document.getElementById('script-output').innerHTML=html;
}

function copyScript(){
  navigator.clipboard.writeText(S.generatedScript).then(function(){
    var btn=document.getElementById('copy-btn');
    btn.textContent='✓ Copiado';
    setTimeout(function(){btn.innerHTML='📋 Copiar';},2000);
  });
}

function downloadScript(){
  var blob=new Blob([S.generatedScript],{type:'text/plain'});
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='run_analysis.py';
  a.click();
}

// ── UTILS ─────────────────────────────────────────────────────────────────────
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function showAlert(id,type,msg){var a=document.getElementById(id);a.className='alert alert-'+type+' show';document.getElementById(id+'-msg').textContent=msg;}
function hideAlert(id){document.getElementById(id).classList.remove('show');}
</script>
</body>
</html>
