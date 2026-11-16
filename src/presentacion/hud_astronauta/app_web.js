// ===================================================================================
//  MOTOR ASÍNCRONO SPA — ASTRO_MED_HUD (SIN CLAVE + BILINGÜE ES/EN + NASA MEASURES)
// ===================================================================================

const HOST_LAN = window.location.hostname || "127.0.0.1";
const API_BASE = `http://${HOST_LAN}:8000/api`;

let idiomaActual = "es";
let misionActiva = "ARTEMIS_LUNA";
let sesionOperador = null;
let tripulantesCache = [];
let botiquinCache = [];
let analiticaActual = null;
let sistemaSeleccionadoActual = "NEURO_PSICO";
let ultimoDiagnosticoSistemas = {
    NEURO_PSICO: "NOMINAL",
    CARDIO_RAD: "NOMINAL",
    METABOLICO_INMUNE: "NOMINAL",
    MUSCULO_ESQUELETICO: "NOMINAL"
};

const META_MISIONES = {
    ARTEMIS_LUNA: {
        es: { chip: "🌕 ARTEMIS LUNAR (1/6 G)", delay: "📡 LATENCIA: 1.3s" },
        en: { chip: "🌕 ARTEMIS LUNAR (1/6 G)", delay: "📡 DELAY: 1.3s" }
    },
    ARES_MARTE: {
        es: { chip: "🔴 ARES MARTE (3/8 G)", delay: "📡 LATENCIA: 22 min" },
        en: { chip: "🔴 ARES MARS (3/8 G)", delay: "📡 DELAY: 22 min" }
    },
    EUROPA_JUPITER: {
        es: { chip: "❄️ CRIO-EUROPA (JÚPITER)", delay: "📡 LATENCIA: 45 min" },
        en: { chip: "❄️ CRYO-EUROPA (JUPITER)", delay: "📡 DELAY: 45 min" }
    }
};

const I18N_WEB = {
    es: {
        login_subtitulo: "Terminal Biométrica Autónoma sin Contraseña para Tripulación en Misión",
        login_perfil: "Seleccioná tu Perfil de Astronauta (Acceso Directo EveryWear):",
        login_entrar: "ABRIR MI HUD BIOMÉTRICO",
        acceso_rapido: "Ingreso 1-Clic:",
        sel_tripulante: "Tripulante Monitoreado:",
        sel_entorno: "Entorno Operativo (5 Peligros):",
        racha_titulo: "RACHA VITAL",
        dias_sol: "Días Sol",
        btn_salir: "Cambiar Tripulante",
        gemelo_titulo: "GEMELO DIGITAL ANATÓMICO",
        gemelo_inst: "Hacé clic en cada zona del cuerpo para inspeccionar Medidas Estándar NASA, impacto espacial y diagnóstico.",
        triage_titulo: "DIAGNÓSTICO AUTÓNOMO DE MISIÓN (NASA STANDARD MEASURES)",
        protocolo_guia: "📋 Protocolo e Instrucciones Paso a Paso (Guía para Tripulación):",
        tierra_critico: "📡 ALERTA MÉDICOS EN TIERRA (Paquete Prioritario)",
        tierra_ok: "🛡️ Autonomía Local Activa",
        kpi_pa: "Presión Arterial (MAP)",
        kpi_fc: "Frecuencia Cardíaca",
        kpi_glu: "Perfil Bioquímico (Glucosa)",
        kpi_temp: "Temperatura / Radiación",
        kpi_sueno: "Actigrafía Sueño / Ánimo",
        kpi_ejer: "Ejercicio ARED / IMTP",
        grafico_titulo: "EVOLUCIÓN TEMPORAL DE INDICADORES (15 DÍAS SOL)",
        grafico_sub: "Incluye bandas de umbral clínico NASA HRP y valores puntuales por Sol",
        mision_tit: "CAMBIAR MISIÓN ESPACIAL ACTIVA",
        mision_sub: "Conmutá la base de datos entre los 3 escenarios interplanetarios:",
        sim_tit: "SIMULADOR DE PELIGROS NASA",
        sim_sub: "Dispará una anomalía en vivo para evaluar la respuesta del CDSS:",
        sim_rad: "☢️ Tormenta Solar (0G)",
        sim_psy: "🧠 Fatiga / Pulsar Test",
        sim_met: "🩸 Hipoglucemia + Fiebre",
        sim_mus: "🦴 Déficit IMTP / 0G",
        form_tit: "REGISTRAR MEDIDAS ESTÁNDAR (EVERYWEAR)",
        in_sis: "Sistólica (mmHg)",
        in_dia: "Diastólica (mmHg)",
        in_fc: "Pulso (BPM)",
        in_glu: "Glucosa (mg/dL)",
        in_temp: "Temp (°C)",
        in_sueno: "Actigrafía Sueño (h)",
        in_animo: "Ánimo / Cohesión (1-5)",
        in_ejer: "Ejercicio / IMTP (min)",
        in_rad: "Radiación (mSv)",
        in_evid: "Estudio / Medida Estándar",
        in_insumo: "Aplicar Insumo del Botiquín (Opcional):",
        btn_submit: "REGISTRAR Y EJECUTAR TRIAGE",
        botiquin_tit: "📦 STOCK BOTIQUÍN A BORDO",
        organos: {
            NEURO_PSICO: {
                titulo: "🧠 Sistema Neuro-Psicológico, Cognitivo y Vestibular",
                peligros: "Medidas Estándar NASA: Pulsar Cognition (10 pruebas) + Actiwatch Spectrum Plus + Cinetosis (0-20).",
                explicacion: "Evalúa aprendizaje visual, memoria, atención vigilante y toma de decisiones de riesgo mediante la batería Pulsar Cognition, encuestas de sueño/cohesión en iPad (EveryWear) y escala de mareo por movimiento (0 = bien, 20 = vómitos) pos-Crew-8."
            },
            CARDIO_RAD: {
                titulo: "❤️ Sistema Cardiovascular, Ortostático y Dosimetría",
                peligros: "Medidas Estándar NASA: Ecografía Carótida (Íntima-Media) + Analitos Cardíacos + Bipedestación 3.5 min.",
                explicacion: "Monitorea el grosor íntima-media carotídeo por ultrasonido, presión arterial media (MAP), respuesta ortostática en prueba de recuperación tras caída/bipedestación y daño endotelial por radiación cósmica o solar."
            },
            METABOLICO_INMUNE: {
                titulo: "🩸 Sistema Metabólico, Inmunitario y Microbioma",
                peligros: "Medidas Estándar NASA: Panel Bioquímico + Inmunidad Innata/Adaptativa (Tubos ACD/Saliva) + Microbioma.",
                explicacion: "Reemplaza el envío de tubos de sangre ACD y suero congelado a la Tierra por análisis en el punto de atención: controla glucosa (mg/dL), fiebre por reactivación viral (Epstein-Barr) y alteraciones del microbioma en entornos cerrados."
            },
            MUSCULO_ESQUELETICO: {
                titulo: "🦴 Sistema Músculo-Esquelético y Sensoriomotor",
                peligros: "Medidas Estándar NASA: Tracción Isométrica a Medio Muslo (IMTP) + Sit-to-Stand + Caminata en Tándem.",
                explicacion: "Evalúa la fuerza muscular isométrica (IMTP), la carga diaria en máquina resistiva ARED y el equilibrio pos-aterrizaje mediante caminata con giro (obstáculo de 30 cm) y 10 pasos talón-punta (Tandem Walk)."
            }
        }
    },
    en: {
        login_subtitulo: "Passwordless Autonomous Biometric Terminal for In-Flight Crew",
        login_perfil: "Select Your Astronaut Profile (EveryWear Direct Access):",
        login_entrar: "OPEN MY BIOMETRIC HUD",
        acceso_rapido: "1-Click Access:",
        sel_tripulante: "Monitored Crew Member:",
        sel_entorno: "Operational Environment (5 Hazards):",
        racha_titulo: "VITAL STREAK",
        dias_sol: "Sol Days",
        btn_salir: "Switch Crew Member",
        gemelo_titulo: "ANATOMICAL DIGITAL TWIN",
        gemelo_inst: "Click on each body region to inspect NASA Standard Measures, spaceflight impact, and triage.",
        triage_titulo: "AUTONOMOUS MISSION DIAGNOSIS (NASA STANDARD MEASURES)",
        protocolo_guia: "📋 Step-by-Step Guided Protocol (Crew Instructions):",
        tierra_critico: "📡 FLIGHT SURGEON ALERT (Priority Telemetry Packet)",
        tierra_ok: "🛡️ Local Autonomy Active",
        kpi_pa: "Blood Pressure (MAP)",
        kpi_fc: "Heart Rate",
        kpi_glu: "Biochemical Profile (Glucose)",
        kpi_temp: "Temperature / Radiation",
        kpi_sueno: "Actigraphy Sleep / Mood",
        kpi_ejer: "ARED Exercise / IMTP",
        grafico_titulo: "TEMPORAL INDICATOR EVOLUTION (15 SOL DAYS)",
        grafico_sub: "Includes NASA HRP clinical threshold bands and Sol data labels",
        mision_tit: "SWITCH ACTIVE SPACE MISSION",
        mision_sub: "Switch database between the 3 interplanetary scenarios:",
        sim_tit: "NASA 5 HAZARDS SIMULATOR",
        sim_sub: "Trigger a live anomaly to evaluate autonomous CDSS response:",
        sim_rad: "☢️ Solar Storm (0G)",
        sim_psy: "🧠 Fatigue / Pulsar Test",
        sim_met: "🩸 EVA Hypoglycemia + Fever",
        sim_mus: "🦴 IMTP / 0G Deficit",
        form_tit: "LOG STANDARD MEASURES (EVERYWEAR)",
        in_sis: "Systolic (mmHg)",
        in_dia: "Diastolic (mmHg)",
        in_fc: "Pulse (BPM)",
        in_glu: "Glucose (mg/dL)",
        in_temp: "Temp (°C)",
        in_sueno: "Actigraphy Sleep (h)",
        in_animo: "Mood / Cohesion (1-5)",
        in_ejer: "Exercise / IMTP (min)",
        in_rad: "Radiation (mSv)",
        in_evid: "Study / Standard Measure",
        in_insumo: "Apply Medical Kit Supply (Optional):",
        btn_submit: "LOG & RUN AUTONOMOUS TRIAGE",
        botiquin_tit: "📦 ON-BOARD MEDICAL KIT STOCK",
        organos: {
            NEURO_PSICO: {
                titulo: "🧠 Neuro-Psychological, Cognitive & Vestibular System",
                peligros: "NASA Standard Measures: Pulsar Cognition (10 tests) + Actiwatch Spectrum Plus + Motion Sickness (0-20).",
                explicacion: "Evaluates visual learning, working memory, vigilant attention, and risk decision-making via Pulsar Cognition software, EveryWear iPad sleep/team cohesion surveys, and post-Crew-8 motion sickness scale (0 = well, 20 = vomiting)."
            },
            CARDIO_RAD: {
                titulo: "❤️ Cardiovascular, Orthostatic & Radiation Dosimetry",
                peligros: "NASA Standard Measures: Carotid Ultrasound (Intima-Media) + Cardiac Analytes + 3.5-min Stand Test.",
                explicacion: "Monitors carotid intima-media thickness via ultrasound, Mean Arterial Pressure (MAP), orthostatic tolerance during recovery-from-fall/stand tests, and vascular endothelial stress from solar/cosmic radiation."
            },
            METABOLICO_INMUNE: {
                titulo: "🩸 Metabolic, Immune Function & Microbiome System",
                peligros: "NASA Standard Measures: Biochem Panel + Innate/Adaptive Immunity (ACD Blood/Saliva) + Microbiome Swabs.",
                explicacion: "Replaces Earth-return frozen serum and 48h ACD blood tubes with point-of-care autonomous triage: tracks blood glucose (mg/dL), febrile immune responses (Epstein-Barr reactivation), and closed-habitat microbiome shifts."
            },
            MUSCULO_ESQUELETICO: {
                titulo: "🦴 Musculoskeletal & Sensorimotor Performance",
                peligros: "NASA Standard Measures: Isometric Mid-Thigh Pull (IMTP) + Sit-to-Stand + Tandem Walk.",
                explicacion: "Assesses lower-body isometric strength (IMTP), daily ARED resistive exercise countermeasure minutes, and post-landing balance via Sit-to-Stand walk-and-turn (30 cm obstacle) and 10-step heel-to-toe Tandem Walk."
            }
        }
    }
};

window.addEventListener("DOMContentLoaded", async () => {
    try {
        const [respIdioma, respTrip] = await Promise.all([
            fetch(`${API_BASE}/idioma`),
            fetch(`${API_BASE}/tripulantes`)
        ]);
        if (respIdioma.ok) {
            const dataId = await respIdioma.json();
            aplicarIdiomaLocal(dataId.idioma || "es");
        }
        if (respTrip.ok) {
            tripulantesCache = await respTrip.json();
            poblarSelectorLoginSinClave();
        }
    } catch (e) {
        aplicarIdiomaLocal("es");
    }
});

function poblarSelectorLoginSinClave() {
    if (!tripulantesCache || tripulantesCache.length === 0) return;
    const sel = document.getElementById("login-usuario");
    sel.innerHTML = "";
    tripulantesCache.forEach(t => {
        const opt = document.createElement("option");
        opt.value = t.usuario;
        opt.textContent = `${t.codigo_astronauta} — ${t.nombres} ${t.apellidos} (${t.rol})`;
        sel.appendChild(opt);
    });
}

async function cambiarIdiomaHUD(nuevoIdioma) {
    aplicarIdiomaLocal(nuevoIdioma);
    try {
        await fetch(`${API_BASE}/idioma`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idioma: nuevoIdioma })
        });
    } catch (e) {}
}

function actualizarBadgesMision() {
    const infoM = (META_MISIONES[misionActiva] || META_MISIONES.ARTEMIS_LUNA)[idiomaActual];
    const bMis = document.getElementById("badge-mision-activa");
    const bLat = document.getElementById("badge-latencia");
    if (bMis) bMis.textContent = infoM.chip;
    if (bLat) bLat.textContent = infoM.delay;
}

function aplicarIdiomaLocal(cod) {
    idiomaActual = cod === "en" ? "en" : "es";
    const d = I18N_WEB[idiomaActual];

    document.getElementById("select-idioma-login").value = idiomaActual;
    document.getElementById("select-idioma-hud").value = idiomaActual;

    const mapaTextos = {
        "lbl-login-subtitulo": d.login_subtitulo,
        "lbl-login-perfil": d.login_perfil,
        "btn-login-entrar": d.login_entrar,
        "lbl-acceso-rapido": d.acceso_rapido,
        "lbl-sel-tripulante": d.sel_tripulante,
        "lbl-sel-entorno": d.sel_entorno,
        "lbl-racha-titulo": d.racha_titulo,
        "btn-salir-hud": d.btn_salir,
        "lbl-gemelo-titulo": d.gemelo_titulo,
        "lbl-gemelo-inst": d.gemelo_inst,
        "triage-titulo": d.triage_titulo,
        "lbl-protocolo-guia": d.protocolo_guia,
        "lbl-kpi-pa": d.kpi_pa,
        "lbl-kpi-fc": d.kpi_fc,
        "lbl-kpi-glu": d.kpi_glu,
        "lbl-kpi-temp": d.kpi_temp,
        "lbl-kpi-sueno": d.kpi_sueno,
        "lbl-kpi-ejer": d.kpi_ejer,
        "lbl-grafico-titulo": d.grafico_titulo,
        "lbl-grafico-sub": d.grafico_sub,
        "lbl-mision-activa-tit": d.mision_tit,
        "lbl-mision-activa-sub": d.mision_sub,
        "lbl-sim-peligros-tit": d.sim_tit,
        "lbl-sim-peligros-sub": d.sim_sub,
        "btn-sim-rad": d.sim_rad,
        "btn-sim-psy": d.sim_psy,
        "btn-sim-met": d.sim_met,
        "btn-sim-mus": d.sim_mus,
        "lbl-form-tit": d.form_tit,
        "lbl-in-sis": d.in_sis,
        "lbl-in-dia": d.in_dia,
        "lbl-in-fc": d.in_fc,
        "lbl-in-glu": d.in_glu,
        "lbl-in-temp": d.in_temp,
        "lbl-in-sueno": d.in_sueno,
        "lbl-in-animo": d.in_animo,
        "lbl-in-ejer": d.in_ejer,
        "lbl-in-rad": d.in_rad,
        "lbl-in-evid": d.in_evid,
        "lbl-in-insumo": d.in_insumo,
        "btn-submit-tel": d.btn_submit,
        "lbl-botiquin-tit": d.botiquin_tit
    };

    Object.entries(mapaTextos).forEach(([id, txt]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = txt;
    });

    actualizarBadgesMision();
    seleccionarSistema(sistemaSeleccionadoActual);
    if (analiticaActual) dibujarGraficoEvolucion();
}

async function ingresoDirecto(usuarioSeleccionado) {
    document.getElementById("login-usuario").value = usuarioSeleccionado;
    await ejecutarIngresoHUD(usuarioSeleccionado);
}

document.getElementById("form-login").addEventListener("submit", async (e) => {
    e.preventDefault();
    const usuario = document.getElementById("login-usuario").value.trim();
    await ejecutarIngresoHUD(usuario);
});

async function ejecutarIngresoHUD(usuario) {
    const lblError = document.getElementById("login-error");
    lblError.textContent = "";

    try {
        if (tripulantesCache.length === 0) {
            const resp = await fetch(`${API_BASE}/tripulantes`);
            tripulantesCache = await resp.json();
        }
        const perfil = tripulantesCache.find(t => t.usuario === usuario) || tripulantesCache[0];
        if (!perfil) throw new Error("No se encontraron perfiles activos en la misión.");

        sesionOperador = perfil;
        document.getElementById("vista-login").classList.add("oculto");
        document.getElementById("vista-hud").classList.remove("oculto");
        document.getElementById("lbl-operador").textContent =
            `${sesionOperador.codigo_astronauta} // ${sesionOperador.nombres} ${sesionOperador.apellidos} (${sesionOperador.rol})`;

        await inicializarDatosHUD();
    } catch (err) {
        lblError.textContent = err.message;
    }
}

function cerrarSesion() {
    sesionOperador = null;
    document.getElementById("vista-hud").classList.add("oculto");
    document.getElementById("vista-login").classList.remove("oculto");
}

async function inicializarDatosHUD() {
    await Promise.all([cargarTripulantes(), cargarBotiquin()]);
    await cambiarTripulanteActivo();
}

async function cargarTripulantes() {
    const resp = await fetch(`${API_BASE}/tripulantes`);
    tripulantesCache = await resp.json();
    const select = document.getElementById("select-tripulante");
    select.innerHTML = "";

    tripulantesCache.forEach(t => {
        const opt = document.createElement("option");
        opt.value = t.id;
        opt.textContent = `${t.codigo_astronauta} — ${t.nombres} ${t.apellidos} (${t.especialidad})`;
        if (sesionOperador && t.id === sesionOperador.id) opt.selected = true;
        select.appendChild(opt);
    });
}

async function cargarBotiquin() {
    const resp = await fetch(`${API_BASE}/botiquin`);
    botiquinCache = await resp.json();

    const selectInsumo = document.getElementById("in-insumo");
    const listaUl = document.getElementById("lista-botiquin");
    selectInsumo.innerHTML = '<option value="">-- Ninguno / None --</option>';
    listaUl.innerHTML = "";

    botiquinCache.forEach(ins => {
        const opt = document.createElement("option");
        opt.value = ins.id;
        opt.textContent = `${ins.codigo} - ${ins.nombre} (Stock: ${ins.stock_actual})`;
        selectInsumo.appendChild(opt);

        const li = document.createElement("li");
        li.innerHTML = `<span><strong>${ins.codigo}</strong> ${ins.nombre}</span> <b>${ins.stock_actual} ${ins.unidad_medida}</b>`;
        listaUl.appendChild(li);
    });
}

async function cambiarTripulanteActivo() {
    const d = I18N_WEB[idiomaActual];
    const idTripulante = parseInt(document.getElementById("select-tripulante").value);
    const tripulante = tripulantesCache.find(t => t.id === idTripulante);
    if (tripulante) {
        document.getElementById("lbl-racha").textContent = `${tripulante.racha_autocuidado} ${d.dias_sol}`;
    }

    const [respHist, respBi] = await Promise.all([
        fetch(`${API_BASE}/telemetria/tripulante/${idTripulante}?limite=15`),
        fetch(`${API_BASE}/analitica/${idTripulante}`)
    ]);

    const historial = await respHist.json();
    analiticaActual = await respBi.json();

    if (historial.length > 0) {
        const ultima = historial[0];
        document.getElementById("select-entorno").value = ultima.entorno;
        renderizarUltimaLectura(ultima);
    }
    dibujarGraficoEvolucion();
}

function actualizarBarraKPI(idBarra, porcentaje, estado) {
    const el = document.getElementById(idBarra);
    if (!el) return;
    const pct = Math.max(8, Math.min(100, porcentaje));
    el.style.width = `${pct}%`;
    if (estado === "CRITICO") el.style.backgroundColor = "#F44336";
    else if (estado === "PRECAUCION") el.style.backgroundColor = "#FF9800";
    else el.style.backgroundColor = "#4CAF50";
}

function renderizarUltimaLectura(lectura, diagnosticoExplicito = null) {
    const d = I18N_WEB[idiomaActual];
    document.getElementById("kpi-presion").textContent = `${lectura.presion_sistolica} / ${lectura.presion_diastolica}`;
    document.getElementById("kpi-map").textContent = `MAP: ${lectura.presion_media} mmHg`;
    document.getElementById("kpi-fc").textContent = `${lectura.frecuencia_cardiaca} BPM`;
    document.getElementById("kpi-glucosa").textContent = `${lectura.glucosa_mg_dl} mg/dL`;
    document.getElementById("kpi-temp").textContent = `${lectura.temperatura_c} °C`;
    document.getElementById("kpi-rad").textContent = `Rad: ${lectura.radiacion_msv} mSv`;
    document.getElementById("kpi-sueno").textContent = `${lectura.horas_sueno} hs`;
    document.getElementById("kpi-animo").textContent = `Mood: ${lectura.estado_animo} / 5`;
    document.getElementById("kpi-ejercicio").textContent = `${lectura.minutos_ejercicio} min`;
    document.getElementById("kpi-evidencia").textContent = `Ref: ${lectura.evidencia_adjunta}`;

    // Actualizar micro-barras de estado en tarjetas KPI
    const estPa = (lectura.presion_sistolica >= 150 || lectura.presion_sistolica < 90) ? "CRITICO" : (lectura.presion_sistolica >= 135 ? "PRECAUCION" : "NOMINAL");
    const estFc = (lectura.frecuencia_cardiaca >= 115 || lectura.frecuencia_cardiaca < 50) ? "CRITICO" : (lectura.frecuencia_cardiaca >= 95 ? "PRECAUCION" : "NOMINAL");
    const estGlu = (lectura.glucosa_mg_dl < 65 || lectura.glucosa_mg_dl > 160) ? "CRITICO" : (lectura.glucosa_mg_dl < 75 || lectura.glucosa_mg_dl > 125 ? "PRECAUCION" : "NOMINAL");
    const estRad = lectura.radiacion_msv >= 2.0 ? "CRITICO" : (lectura.radiacion_msv >= 0.8 ? "PRECAUCION" : "NOMINAL");
    const estSue = lectura.horas_sueno < 5.0 ? "CRITICO" : (lectura.horas_sueno < 6.2 ? "PRECAUCION" : "NOMINAL");
    const estEje = lectura.minutos_ejercicio < 15 ? "CRITICO" : (lectura.minutos_ejercicio < 35 ? "PRECAUCION" : "NOMINAL");

    actualizarBarraKPI("bar-pa", (lectura.presion_sistolica / 180) * 100, estPa);
    actualizarBarraKPI("bar-fc", (lectura.frecuencia_cardiaca / 150) * 100, estFc);
    actualizarBarraKPI("bar-glu", (lectura.glucosa_mg_dl / 180) * 100, estGlu);
    actualizarBarraKPI("bar-rad", (lectura.radiacion_msv / 3.5) * 100, estRad);
    actualizarBarraKPI("bar-sueno", (lectura.horas_sueno / 9.0) * 100, estSue);
    actualizarBarraKPI("bar-ejer", (lectura.minutos_ejercicio / 90) * 100, estEje);

    const claseAlerta = lectura.nivel_alerta.toLowerCase();
    const badgeGlobal = document.getElementById("badge-global");
    badgeGlobal.textContent = lectura.nivel_alerta;
    badgeGlobal.className = `badge ${claseAlerta}`;

    const panelProtocolo = document.getElementById("panel-protocolo");
    panelProtocolo.className = `bloque-triage ${claseAlerta}`;
    document.getElementById("triage-resumen").textContent = lectura.diagnostico_resumen;
    document.getElementById("triage-instruccion").textContent = lectura.instruccion_accion;

    const tagTierra = document.getElementById("triage-tierra");
    if (lectura.nivel_alerta === "CRITICO") {
        tagTierra.textContent = d.tierra_critico;
        tagTierra.style.color = "#F44336";
    } else {
        tagTierra.textContent = d.tierra_ok;
        tagTierra.style.color = "#38bdf8";
    }

    const sistemas = ["NEURO_PSICO", "CARDIO_RAD", "METABOLICO_INMUNE", "MUSCULO_ESQUELETICO"];
    sistemas.forEach(sis => {
        let estadoZona = "NOMINAL";
        if (diagnosticoExplicito && diagnosticoExplicito.estado_sistemas) {
            estadoZona = diagnosticoExplicito.estado_sistemas[sis] || "NOMINAL";
        } else if (lectura.sistema_afectado === sis) {
            estadoZona = lectura.nivel_alerta;
        }
        ultimoDiagnosticoSistemas[sis] = estadoZona;
        const nodoSvg = document.getElementById(`zona-${sis}`);
        if (nodoSvg) {
            nodoSvg.setAttribute("class", `zona-clicable ${estadoZona.toLowerCase()}`);
        }
        const pill = document.getElementById(`pill-${sis}`);
        if (pill) {
            pill.className = `pill-sistema ${estadoZona.toLowerCase()}`;
        }
    });

    if (lectura.sistema_afectado && lectura.sistema_afectado !== "NINGUNO") {
        seleccionarSistema(lectura.sistema_afectado);
    }
}

function seleccionarSistema(codigoSistema) {
    sistemaSeleccionadoActual = codigoSistema;
    const d = I18N_WEB[idiomaActual];
    const info = d.organos[codigoSistema];
    if (!info) return;
    const estadoActual = ultimoDiagnosticoSistemas[codigoSistema] || "NOMINAL";
    document.getElementById("titulo-organo").textContent = `${info.titulo} [${estadoActual}]`;
    document.getElementById("desc-organo").innerHTML =
        `<strong>${info.peligros}</strong><br>${info.explicacion}`;
}

function actualizarInfoEntorno() {
    const entorno = document.getElementById("select-entorno").value;
    document.getElementById("titulo-organo").textContent =
        idiomaActual === "en" ? `Selected Environment: ${entorno}` : `Entorno Seleccionado: ${entorno}`;
    document.getElementById("desc-organo").textContent =
        idiomaActual === "en"
            ? "Rule engine automatically adjusted sleep, radiation, blood pressure, and IMTP/ARED exercise thresholds."
            : "El motor de reglas ajustó automáticamente los umbrales de sueño, radiación, presión y ejercicio ARED/IMTP.";
}

document.getElementById("form-telemetria").addEventListener("submit", async (e) => {
    e.preventDefault();
    const d = I18N_WEB[idiomaActual];
    const idTripulante = parseInt(document.getElementById("select-tripulante").value);
    const idInsumoVal = document.getElementById("in-insumo").value;

    const payload = {
        id_tripulante: idTripulante,
        entorno: document.getElementById("select-entorno").value,
        presion_sistolica: parseInt(document.getElementById("in-sistolica").value),
        presion_diastolica: parseInt(document.getElementById("in-diastolica").value),
        frecuencia_cardiaca: parseInt(document.getElementById("in-fc").value),
        glucosa_mg_dl: parseFloat(document.getElementById("in-glucosa").value),
        temperatura_c: parseFloat(document.getElementById("in-temp").value),
        horas_sueno: parseFloat(document.getElementById("in-sueno").value),
        estado_animo: parseInt(document.getElementById("in-animo").value),
        minutos_ejercicio: parseInt(document.getElementById("in-ejercicio").value),
        radiacion_msv: parseFloat(document.getElementById("in-rad").value),
        evidencia_adjunta: document.getElementById("in-evidencia").value,
        id_insumo_aplicado: idInsumoVal ? parseInt(idInsumoVal) : null,
        cantidad_insumo: parseFloat(document.getElementById("in-cant-insumo").value || 0)
    };

    try {
        const resp = await fetch(`${API_BASE}/telemetria`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Operador-Id": sesionOperador ? String(sesionOperador.id) : "1"
            },
            body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detalle || "Error al registrar telemetría");

        document.getElementById("lbl-racha").textContent = `${data.racha_actualizada} ${d.dias_sol}`;
        await cargarTripulantes();
        document.getElementById("select-tripulante").value = idTripulante;
        await cargarBotiquin();
        renderizarUltimaLectura(data.lectura, data.diagnostico);

        const respBi = await fetch(`${API_BASE}/analitica/${idTripulante}`);
        analiticaActual = await respBi.json();
        dibujarGraficoEvolucion();
    } catch (err) {
        alert("Alerta del Sistema: " + err.message);
    }
});

async function simularCrisis(escenario) {
    const d = I18N_WEB[idiomaActual];
    const idTripulante = parseInt(document.getElementById("select-tripulante").value);
    const resp = await fetch(`${API_BASE}/telemetria/simular-crisis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_tripulante: idTripulante, escenario })
    });
    const data = await resp.json();
    if (resp.ok) {
        document.getElementById("select-entorno").value = data.lectura.entorno;
        document.getElementById("lbl-racha").textContent = `${data.racha_actualizada} ${d.dias_sol}`;
        renderizarUltimaLectura(data.lectura, data.diagnostico);
        const respBi = await fetch(`${API_BASE}/analitica/${idTripulante}`);
        analiticaActual = await respBi.json();
        dibujarGraficoEvolucion();
    }
}

async function cambiarMision(codigoMision) {
    const resp = await fetch(`${API_BASE}/telemetria/cargar-mision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mision: codigoMision })
    });
    if (resp.ok) {
        misionActiva = codigoMision;
        actualizarBadgesMision();
        await inicializarDatosHUD();
    }
}

function dibujarGraficoEvolucion() {
    const canvas = document.getElementById("canvas-evolucion");
    if (!canvas || !analiticaActual || !analiticaActual.series) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    const metrica = document.getElementById("select-metrica-grafico").value;
    const valores = analiticaActual.series[metrica] || [];
    if (valores.length === 0) return;

    const esCardioDual = metrica === "frecuencia_cardiaca" && Array.isArray(analiticaActual.series.presion_sistolica);
    const serieSecundaria = esCardioDual ? analiticaActual.series.presion_sistolica : [];

    const todosValores = esCardioDual ? valores.concat(serieSecundaria) : valores;
    const padL = 46, padR = 24, padT = 28, padB = 32;
    const minVal = Math.min(...todosValores) * 0.88;
    const maxVal = Math.max(...todosValores) * 1.12 || 10;

    const posX = (i) => padL + (i / Math.max(valores.length - 1, 1)) * (W - padL - padR);
    const posY = (v) => padT + (1 - (v - minVal) / (maxVal - minVal || 1)) * (H - padT - padB);

    // 1. Grilla horizontal y vertical táctica
    ctx.strokeStyle = "rgba(30, 41, 59, 0.85)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padT + ((H - padT - padB) / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(W - padR, y);
        ctx.stroke();

        const valEtiqueta = (maxVal - ((maxVal - minVal) / 4) * i).toFixed(0);
        ctx.fillStyle = "#94a3b8";
        ctx.font = "11px Segoe UI, sans-serif";
        ctx.fillText(valEtiqueta, 8, y + 4);
    }

    // 2. Línea de Umbral Clínico NASA HRP (Punteada)
    let umbralAlerta = null;
    let etiquetaUmbral = "";
    if (metrica === "frecuencia_cardiaca") {
        umbralAlerta = 100;
        etiquetaUmbral = "NASA Max HR (100 BPM)";
    } else if (metrica === "glucosa_mg_dl") {
        umbralAlerta = 70;
        etiquetaUmbral = "Hypoglycemia Limit (70 mg/dL)";
    } else if (metrica === "horas_sueno") {
        umbralAlerta = 6.0;
        etiquetaUmbral = "Min Circadian Sleep (6.0 h)";
    }

    if (umbralAlerta !== null && umbralAlerta >= minVal && umbralAlerta <= maxVal) {
        const yUmbral = posY(umbralAlerta);
        ctx.save();
        ctx.setLineDash([5, 5]);
        ctx.strokeStyle = "rgba(244, 67, 54, 0.75)";
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        ctx.moveTo(padL, yUmbral);
        ctx.lineTo(W - padR, yUmbral);
        ctx.stroke();
        ctx.fillStyle = "#fca5a5";
        ctx.font = "10px Segoe UI, sans-serif";
        ctx.fillText(etiquetaUmbral, W - padR - 155, yUmbral - 5);
        ctx.restore();
    }

    // 3. Área degradada bajo la serie principal
    const grad = ctx.createLinearGradient(0, padT, 0, H - padB);
    grad.addColorStop(0, "rgba(56, 189, 248, 0.32)");
    grad.addColorStop(1, "rgba(56, 189, 248, 0.0)");

    ctx.beginPath();
    valores.forEach((v, i) => {
        if (i === 0) ctx.moveTo(posX(i), posY(v));
        else ctx.lineTo(posX(i), posY(v));
    });
    ctx.lineTo(posX(valores.length - 1), H - padB);
    ctx.lineTo(posX(0), H - padB);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // 4. Segunda curva (Presión Sistólica) cuando está activa la vista cardiovascular
    if (esCardioDual && serieSecundaria.length > 0) {
        ctx.strokeStyle = "#a855f7";
        ctx.lineWidth = 2;
        ctx.beginPath();
        serieSecundaria.forEach((v, i) => {
            if (i === 0) ctx.moveTo(posX(i), posY(v));
            else ctx.lineTo(posX(i), posY(v));
        });
        ctx.stroke();
    }

    // 5. Trazado de la curva principal
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 2.6;
    ctx.beginPath();
    valores.forEach((v, i) => {
        if (i === 0) ctx.moveTo(posX(i), posY(v));
        else ctx.lineTo(posX(i), posY(v));
    });
    ctx.stroke();

    // 6. Puntos de telemetría, etiquetas de Sol y valores sobre los nodos
    valores.forEach((v, i) => {
        const x = posX(i);
        const y = posY(v);
        const esUltimo = i === valores.length - 1;

        ctx.fillStyle = esUltimo ? "#FF9800" : "#38bdf8";
        ctx.beginPath();
        ctx.arc(x, y, esUltimo ? 5 : 3.5, 0, Math.PI * 2);
        ctx.fill();

        if (i % 2 === 0 || esUltimo) {
            ctx.fillStyle = esUltimo ? "#fbbf24" : "#e2e8f0";
            ctx.font = esUltimo ? "bold 10px Segoe UI" : "10px Segoe UI";
            ctx.fillText(String(v), x - 8, y - 8);
        }

        if (i % 3 === 0 || esUltimo) {
            ctx.fillStyle = "#64748b";
            ctx.font = "10px Segoe UI";
            ctx.fillText(`S${i + 1}`, x - 6, H - 10);
        }
    });

    // 7. Leyenda superior en el lienzo
    ctx.font = "bold 11px Segoe UI";
    ctx.fillStyle = "#38bdf8";
    ctx.fillText(esCardioDual ? "● Heart Rate (BPM)" : `● ${metrica}`, padL + 6, 16);
    if (esCardioDual) {
        ctx.fillStyle = "#a855f7";
        ctx.fillText("● Systolic BP (mmHg)", padL + 135, 16);
    }
}