# ===========================================================================
#  TABLERO DE ANALÍTICA BIOMÉTRICA Y SERIES TEMPORALES (CAPA 4 - MATPLOTLIB)
# ===========================================================================

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.presentacion.i18n import t
from src.presentacion.consola_comando.cliente_api import ClienteAPIAstroMed


class VentanaAnalitica:
    def __init__(self, master: tk.Toplevel, cliente_api: ClienteAPIAstroMed, id_tripulante_inicial: int = 1):
        self.master = master
        self.api = cliente_api
        self.id_tripulante = id_tripulante_inicial
        self.mapa_tripulantes = {}

        self.master.title(t("bi_titulo_ventana"))
        self.master.geometry("1040x720")
        self.master.configure(bg="#060911")

        # Barra superior con selector de astronauta en vivo
        barra = tk.Frame(self.master, bg="#10182a", pady=10, padx=14, highlightbackground="#1e293b", highlightthickness=1)
        barra.pack(fill="x")

        self.lbl_titulo = tk.Label(
            barra,
            text=t("bi_cabecera", id=self.id_tripulante),
            fg="#38bdf8",
            bg="#10182a",
            font=("Segoe UI", 11, "bold"),
        )
        self.lbl_titulo.pack(side="left")

        selector_frame = tk.Frame(barra, bg="#10182a")
        selector_frame.pack(side="right")

        tk.Label(
            selector_frame, text=t("bi_sel_trip"), fg="#94a3b8", bg="#10182a", font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(0, 6))

        self.combo_trip = ttk.Combobox(selector_frame, state="readonly", width=32)
        self.combo_trip.pack(side="left")
        self.combo_trip.bind("<<ComboboxSelected>>", self._al_cambiar_tripulante)

        # Franja de Resumen de Promedios
        barra_kpi = tk.Frame(self.master, bg="#090d18", pady=6, padx=14)
        barra_kpi.pack(fill="x")

        self.lbl_resumen = tk.Label(
            barra_kpi, text="", fg="#e2e8f0", bg="#090d18", font=("Segoe UI", 9, "bold")
        )
        self.lbl_resumen.pack(anchor="w")

        self.figura = Figure(figsize=(10, 6.0), dpi=100, facecolor="#060911")
        self.canvas = FigureCanvasTkAgg(self.figura, master=self.master)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=8)

        self._poblar_selector_tripulantes()
        self.cargar_y_dibujar()

    def _poblar_selector_tripulantes(self) -> None:
        try:
            lista = self.api.listar_tripulantes()
            opciones = []
            idx_sel = 0
            for idx, tr in enumerate(lista):
                etiqueta = f"{tr['codigo_astronauta']} — {tr['nombres']} {tr['apellidos']}"
                opciones.append(etiqueta)
                self.mapa_tripulantes[etiqueta] = tr["id"]
                if tr["id"] == self.id_tripulante:
                    idx_sel = idx
            if opciones:
                self.combo_trip["values"] = opciones
                self.combo_trip.current(idx_sel)
        except Exception:
            pass

    def _al_cambiar_tripulante(self, _evento=None) -> None:
        etiqueta = self.combo_trip.get()
        if etiqueta in self.mapa_tripulantes:
            self.id_tripulante = self.mapa_tripulantes[etiqueta]
            self.lbl_titulo.configure(text=t("bi_cabecera", id=self.id_tripulante))
            self.cargar_y_dibujar()

    def cargar_y_dibujar(self) -> None:
        datos = self.api.obtener_analitica(self.id_tripulante)
        self.datos_actuales = datos

        prom = datos.get("promedios", {})
        self.lbl_resumen.configure(
            text=t(
                "bi_resumen",
                total=datos.get("total_lecturas", 0),
                fc=prom.get("frecuencia_cardiaca", 0),
                glu=prom.get("glucosa_mg_dl", 0),
                rad=prom.get("radiacion_acumulada_msv", 0),
            )
        )

        self.figura.clear()
        series = datos.get("series", {})
        if not series:
            return

        sistolica = series.get("presion_sistolica", [])
        fc = series.get("frecuencia_cardiaca", [])
        glucosa = series.get("glucosa_mg_dl", [])
        sueno = series.get("horas_sueno", [])
        eje_x = list(range(1, len(sistolica) + 1))

        # SUBPLOT 1: Cardiovascular (Presión Sistólica + Frecuencia Cardíaca + Umbral NASA)
        ax1 = self.figura.add_subplot(211, facecolor="#10182a")
        if sistolica:
            ax1.plot(eje_x, sistolica, label=t("bi_graf1_sis"), color="#38bdf8", linewidth=2.2, marker="o", markersize=5)
            ax1.fill_between(eje_x, sistolica, min(sistolica) * 0.9, color="#38bdf8", alpha=0.14)
            ax1.annotate(
                f"{sistolica[-1]} mmHg",
                xy=(eje_x[-1], sistolica[-1]),
                xytext=(-35, 8),
                textcoords="offset points",
                color="#38bdf8",
                fontsize=8,
                fontweight="bold",
            )
        if fc:
            ax1.plot(eje_x, fc, label=t("bi_graf1_fc"), color="#FF9800", linewidth=2.0, marker="s", markersize=4)
            ax1.annotate(
                f"{fc[-1]} bpm",
                xy=(eje_x[-1], fc[-1]),
                xytext=(-30, -14),
                textcoords="offset points",
                color="#FF9800",
                fontsize=8,
                fontweight="bold",
            )

        ax1.axhline(140, color="#F44336", linestyle="--", linewidth=1.1, alpha=0.75, label="NASA Max BP (140 mmHg)")
        ax1.set_title(t("bi_graf1_tit"), color="#f8fafc", fontsize=10, fontweight="bold", pad=8)
        ax1.tick_params(colors="#94a3b8", labelsize=8)
        ax1.legend(loc="upper left", fontsize=8, facecolor="#090d18", edgecolor="#1e293b", labelcolor="#e2e8f0")
        ax1.grid(True, color="#1e293b", linestyle="--", linewidth=0.8)
        for espina in ax1.spines.values():
            espina.set_color("#1e293b")

        # SUBPLOT 2: Bioquímica (Glucosa) + Actigrafía de Sueño en eje secundario
        ax2 = self.figura.add_subplot(212, facecolor="#10182a")
        if glucosa:
            ax2.plot(eje_x, glucosa, label=t("bi_graf2_glu"), color="#4CAF50", linewidth=2.2, marker="^", markersize=5)
            ax2.fill_between(eje_x, glucosa, 50, color="#4CAF50", alpha=0.12)
            ax2.annotate(
                f"{glucosa[-1]} mg/dL",
                xy=(eje_x[-1], glucosa[-1]),
                xytext=(-40, 8),
                textcoords="offset points",
                color="#4CAF50",
                fontsize=8,
                fontweight="bold",
            )

        ax2.axhline(70, color="#F44336", linestyle="--", linewidth=1.1, alpha=0.75, label="Hypoglycemia Limit (70 mg/dL)")
        ax2.set_title(t("bi_graf2_tit"), color="#f8fafc", fontsize=10, fontweight="bold", pad=8)
        ax2.set_xlabel("Sol Days", color="#94a3b8", fontsize=8)
        ax2.tick_params(colors="#94a3b8", labelsize=8)
        ax2.grid(True, color="#1e293b", linestyle="--", linewidth=0.8)
        for espina in ax2.spines.values():
            espina.set_color("#1e293b")

        if sueno and len(sueno) == len(eje_x):
            ax2_b = ax2.twinx()
            ax2_b.bar(eje_x, sueno, alpha=0.22, color="#a855f7", width=0.45, label=t("bi_graf3_sueno"))
            ax2_b.tick_params(colors="#c084fc", labelsize=8)
            ax2_b.set_ylim(0, 12)
            for espina in ax2_b.spines.values():
                espina.set_color("#1e293b")

        ax2.legend(loc="upper left", fontsize=8, facecolor="#090d18", edgecolor="#1e293b", labelcolor="#e2e8f0")

        self.figura.tight_layout(pad=2.0)
        self.canvas.draw()