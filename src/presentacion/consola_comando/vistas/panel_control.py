# =============================================================================
#  PANEL DE CONTROL DE MISIÓN Y MONITOREO GRUPAL (CAPA 4 - CONSOLA DE COMANDO)
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from src.presentacion.i18n import t
from src.presentacion.consola_comando.cliente_api import ClienteAPIAstroMed, ErrorClienteAPI
from src.presentacion.consola_comando.vistas.analitica import VentanaAnalitica
from src.presentacion.consola_comando.vistas.consola import VentanaConsolaSQL


class VentanaPanelControl:
    def __init__(self, master: tk.Toplevel, cliente_api: ClienteAPIAstroMed, al_cerrar=None):
        self.master = master
        self.api = cliente_api
        self.al_cerrar = al_cerrar

        from src.presentacion.consola_comando.vistas.login import aplicar_tema_aeroespacial
        aplicar_tema_aeroespacial(self.master)

        op = self.api.operador_actual or {"nombres": "Operador", "rol": "Comandante Medico"}
        self.master.title(t("pc_titulo_ventana", nombre=op["nombres"], rol=op["rol"]))
        self.master.geometry("1200x760")
        self.master.configure(bg="#060911")

        if self.al_cerrar:
            self.master.protocol("WM_DELETE_WINDOW", self._cerrar)

        # 1. Barra Superior de Comando
        barra = tk.Frame(self.master, bg="#10182a", pady=10, padx=16, highlightbackground="#1e293b", highlightthickness=1)
        barra.pack(fill="x")

        tk.Label(
            barra,
            text=t("pc_cabecera"),
            fg="#38bdf8",
            bg="#10182a",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        tk.Button(
            barra,
            text=t("pc_btn_sync"),
            bg="#0284c7",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.refrescar_tablero,
        ).pack(side="right", padx=4)

        self.btn_consola = tk.Button(
            barra,
            text=t("pc_btn_sql"),
            bg="#475569",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.abrir_consola_sql,
        )
        self.btn_consola.pack(side="right", padx=4)
        if op.get("rol") == "Especialista de Mision":
            self.btn_consola.configure(state="disabled")

        tk.Button(
            barra,
            text=t("pc_btn_bi"),
            bg="#7c3aed",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.abrir_analitica,
        ).pack(side="right", padx=4)

        # 2. Franja de Tarjetas KPI de Estado del Escuadrón
        marco_kpis = tk.Frame(self.master, bg="#060911", pady=8, padx=14)
        marco_kpis.pack(fill="x")

        self.lbl_kpi_trip = self._crear_tarjeta_kpi(marco_kpis, t("pc_kpi_escuadron"), "7", "#38bdf8")
        self.lbl_kpi_nom = self._crear_tarjeta_kpi(marco_kpis, t("pc_kpi_nominales"), "--", "#4CAF50")
        self.lbl_kpi_aler = self._crear_tarjeta_kpi(marco_kpis, t("pc_kpi_alertas"), "--", "#F44336")
        self.lbl_kpi_racha = self._crear_tarjeta_kpi(marco_kpis, t("pc_kpi_racha"), "-- Sol", "#fbbf24")

        # 3. Barra de Conmutación de Misiones y Simulación de Crisis en 2 columnas
        marco_acciones = tk.Frame(self.master, bg="#10182a", pady=8, padx=14, highlightbackground="#1e293b", highlightthickness=1)
        marco_acciones.pack(fill="x", padx=14, pady=(2, 6))

        # Sub-bloque izquierdo: Misiones
        bloque_mis = tk.Frame(marco_acciones, bg="#10182a")
        bloque_mis.pack(side="left")

        tk.Label(
            bloque_mis,
            text=t("pc_lbl_mision"),
            bg="#10182a",
            fg="#38bdf8",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(0, 6))

        for texto_m, cod_m, col_m in [
            (t("pc_mision_luna"), "ARTEMIS_LUNA", "#0d9488"),
            (t("pc_mision_marte"), "ARES_MARTE", "#ea580c"),
            (t("pc_mision_europa"), "EUROPA_JUPITER", "#2563eb"),
        ]:
            tk.Button(
                bloque_mis,
                text=texto_m,
                bg=col_m,
                fg="white",
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=3,
                command=lambda m=cod_m: self.conmutar_mision(m),
            ).pack(side="left", padx=3)

        # Sub-bloque derecho: Crisis
        bloque_sim = tk.Frame(marco_acciones, bg="#10182a")
        bloque_sim.pack(side="right")

        tk.Label(
            bloque_sim,
            text=t("pc_lbl_crisis"),
            bg="#10182a",
            fg="#cbd5e1",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(0, 6))

        for etiqueta, cod, color in [
            (t("pc_crisis_rad"), "TORMENTA_SOLAR", "#dc2626"),
            (t("pc_crisis_psy"), "CONFINAMIENTO_ROVER", "#7c3aed"),
            (t("pc_crisis_met"), "HIPOGLUCEMIA_EVA", "#d97706"),
            (t("pc_crisis_mus"), "ATROFIA_CERO_G", "#059669"),
        ]:
            tk.Button(
                bloque_sim,
                text=etiqueta,
                bg=color,
                fg="white",
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                cursor="hand2",
                padx=7,
                pady=3,
                command=lambda c=cod: self.disparar_simulacion(c),
            ).pack(side="left", padx=3)

        # 4. Grilla 1: Estado de los Tripulantes
        marco_trip = tk.LabelFrame(
            self.master,
            text=t("pc_marco_trip"),
            bg="#10182a",
            fg="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=6,
        )
        marco_trip.pack(fill="x", padx=14, pady=(2, 6))

        cols_t = ("id", "codigo", "nombre", "rol", "especialidad", "racha")
        self.tabla_tripulantes = ttk.Treeview(marco_trip, columns=cols_t, show="headings", height=7)
        encabezados_t = {
            "id": ("ID", 45),
            "codigo": (t("pc_col_codigo"), 100),
            "nombre": (t("pc_col_nombre"), 220),
            "rol": (t("pc_col_rol"), 180),
            "especialidad": (t("pc_col_esp"), 260),
            "racha": (t("pc_col_racha"), 150),
        }
        for col, (txt, ancho) in encabezados_t.items():
            self.tabla_tripulantes.heading(col, text=txt)
            self.tabla_tripulantes.column(col, width=ancho, anchor="center")
        self.tabla_tripulantes.pack(fill="x", expand=True)

        # 5. Grilla 2: Bitácora Histórica de Lecturas Biométricas y Triage
        marco_tel = tk.LabelFrame(
            self.master,
            text=t("pc_marco_tel"),
            bg="#10182a",
            fg="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=6,
        )
        marco_tel.pack(fill="both", expand=True, padx=14, pady=(2, 10))

        cols_l = ("id", "fecha", "tripulante", "entorno", "pa", "fc", "glucosa", "sueno", "alerta", "sistema", "diagnostico")
        scroll_tel = ttk.Scrollbar(marco_tel, orient="vertical")
        self.tabla_telemetria = ttk.Treeview(
            marco_tel, columns=cols_l, show="headings", height=10, yscrollcommand=scroll_tel.set
        )
        scroll_tel.config(command=self.tabla_telemetria.yview)

        encabezados_l = {
            "id": ("ID", 40),
            "fecha": (t("pc_col_fecha"), 135),
            "tripulante": (t("pc_col_trip"), 65),
            "entorno": (t("pc_col_entorno"), 150),
            "pa": (t("pc_col_pa"), 105),
            "fc": (t("pc_col_fc"), 65),
            "glucosa": (t("pc_col_glu"), 75),
            "sueno": (t("pc_col_sueno"), 60),
            "alerta": (t("pc_col_alerta"), 95),
            "sistema": (t("pc_col_sis"), 135),
            "diagnostico": (t("pc_col_diag"), 340),
        }
        for col, (txt, ancho) in encabezados_l.items():
            self.tabla_telemetria.heading(col, text=txt)
            self.tabla_telemetria.column(col, width=ancho, anchor="center")

        # Etiquetas cromáticas oscuras de alto contraste
        self.tabla_telemetria.tag_configure("NOMINAL", background="#062e22", foreground="#6ee7b7")
        self.tabla_telemetria.tag_configure("PRECAUCION", background="#452205", foreground="#fcd34d")
        self.tabla_telemetria.tag_configure("CRITICO", background="#4c0d14", foreground="#fca5a5")

        self.tabla_telemetria.pack(side="left", fill="both", expand=True)
        scroll_tel.pack(side="right", fill="y")

        self.refrescar_tablero()

    def _crear_tarjeta_kpi(self, padre: tk.Frame, titulo: str, valor_inicial: str, color_acento: str) -> tk.Label:
        card = tk.Frame(
            padre,
            bg="#10182a",
            padx=16,
            pady=8,
            highlightbackground="#1e293b",
            highlightthickness=1,
        )
        card.pack(side="left", fill="x", expand=True, padx=4)

        tk.Label(
            card, text=titulo, fg="#94a3b8", bg="#10182a", font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        lbl_val = tk.Label(
            card, text=valor_inicial, fg=color_acento, bg="#10182a", font=("Segoe UI", 16, "bold")
        )
        lbl_val.pack(anchor="w", pady=(2, 0))
        return lbl_val

    def obtener_id_tripulante_seleccionado(self) -> int:
        sel = self.tabla_tripulantes.selection()
        if sel:
            valores = self.tabla_tripulantes.item(sel[0], "values")
            return int(valores[0])
        items = self.tabla_tripulantes.get_children()
        if items:
            return int(self.tabla_tripulantes.item(items[0], "values")[0])
        return 1

    def refrescar_tablero(self) -> None:
        for item in self.tabla_tripulantes.get_children():
            self.tabla_tripulantes.delete(item)
        for item in self.tabla_telemetria.get_children():
            self.tabla_telemetria.delete(item)

        tripulantes = self.api.listar_tripulantes()
        suma_rachas = 0
        for t_row in tripulantes:
            suma_rachas += int(t_row.get("racha_autocuidado", 0))
            self.tabla_tripulantes.insert(
                "",
                "end",
                values=(
                    t_row["id"],
                    t_row["codigo_astronauta"],
                    f"{t_row['nombres']} {t_row['apellidos']}",
                    t_row["rol"],
                    t_row["especialidad"],
                    f"{t_row['racha_autocuidado']} Sol",
                ),
            )

        lecturas = self.api.listar_telemetria()
        ultimas_por_tripulante = {}
        for l in lecturas:
            id_t = l["id_tripulante"]
            if id_t not in ultimas_por_tripulante:
                ultimas_por_tripulante[id_t] = l["nivel_alerta"]

        for l in lecturas[:45]:
            alerta = l["nivel_alerta"]
            self.tabla_telemetria.insert(
                "",
                "end",
                values=(
                    l["id"],
                    l["fecha"],
                    f"AST-00{l['id_tripulante']}",
                    l["entorno"],
                    f"{l['presion_sistolica']}/{l['presion_diastolica']} ({l['presion_media']})",
                    f"{l['frecuencia_cardiaca']} bpm",
                    f"{l['glucosa_mg_dl']} mg/dL",
                    f"{l['horas_sueno']} h",
                    alerta,
                    l["sistema_afectado"],
                    l["instruccion_accion"],
                ),
                tags=(alerta,),
            )

        # Actualizar Tarjetas KPI
        total_trip = len(tripulantes)
        nominales = sum(1 for est in ultimas_por_tripulante.values() if est == "NOMINAL")
        alertas = sum(1 for est in ultimas_por_tripulante.values() if est in ("PRECAUCION", "CRITICO"))
        prom_racha = round(suma_rachas / max(total_trip, 1), 1)

        self.lbl_kpi_trip.configure(text=str(total_trip))
        self.lbl_kpi_nom.configure(text=str(nominales))
        self.lbl_kpi_aler.configure(text=str(alertas))
        self.lbl_kpi_racha.configure(text=f"{prom_racha} Sol")

    def conmutar_mision(self, codigo_mision: str) -> None:
        try:
            self.api.cambiar_mision(codigo_mision)
            self.refrescar_tablero()
            messagebox.showinfo(t("pc_msg_mision_tit"), t("pc_msg_mision_txt", mision=codigo_mision))
        except ErrorClienteAPI as e:
            messagebox.showerror("Error", str(e))

    def disparar_simulacion(self, escenario: str) -> None:
        id_t = self.obtener_id_tripulante_seleccionado()
        try:
            res = self.api.simular_crisis(id_t, escenario)
            diag = res["diagnostico"]
            self.refrescar_tablero()
            messagebox.showwarning(
                t("pc_msg_triage_tit", nivel=diag["nivel_alerta_global"]),
                f"{t('pc_msg_triage_sis')}: {diag['sistema_afectado_principal']}\n\n"
                f"{t('pc_msg_triage_diag')}: {diag['resumen_clinico']}\n\n"
                f"{t('pc_msg_triage_prot')}: {diag['instruccion_paso_a_paso']}",
            )
        except ErrorClienteAPI as e:
            messagebox.showerror("Error", str(e))

    def abrir_analitica(self) -> None:
        id_t = self.obtener_id_tripulante_seleccionado()
        top = tk.Toplevel(self.master)
        VentanaAnalitica(top, self.api, id_tripulante_inicial=id_t)

    def abrir_consola_sql(self) -> None:
        top = tk.Toplevel(self.master)
        VentanaConsolaSQL(top, self.api)

    def _cerrar(self) -> None:
        self.master.destroy()
        if self.al_cerrar:
            self.al_cerrar()