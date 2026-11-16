# =================================================================
#  CONSOLA DE AUDITORÍA SQL EN CAJA DE ARENA (SANDBOXING - CAPA 4)
# =================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from src.presentacion.i18n import t
from src.presentacion.consola_comando.cliente_api import ClienteAPIAstroMed, ErrorClienteAPI


class VentanaConsolaSQL:
    def __init__(self, master: tk.Toplevel, cliente_api: ClienteAPIAstroMed):
        self.master = master
        self.api = cliente_api

        from src.presentacion.consola_comando.vistas.login import aplicar_tema_aeroespacial
        aplicar_tema_aeroespacial(self.master)

        self.master.title(t("sql_titulo_ventana"))
        self.master.geometry("940x560")
        self.master.configure(bg="#060911")

        # Cabecera e instrucción
        tk.Label(
            self.master,
            text=t("sql_instruccion"),
            bg="#060911",
            fg="#38bdf8",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=14, pady=(12, 4))

        # Barra de Entrada SQL + Botón Ejecutar
        fila_query = tk.Frame(self.master, bg="#060911")
        fila_query.pack(fill="x", padx=14, pady=4)

        self.txt_query = tk.Entry(
            fila_query,
            font=("Consolas", 11),
            bg="#10182a",
            fg="#f8fafc",
            insertbackground="#38bdf8",
            relief="flat",
            highlightbackground="#334155",
            highlightcolor="#38bdf8",
            highlightthickness=1,
        )
        self.txt_query.insert(
            0,
            "SELECT codigo_astronauta, nombres, apellidos, rol, racha_autocuidado FROM vista_tripulacion_activa",
        )
        self.txt_query.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        tk.Button(
            fila_query,
            text=t("sql_btn_ejecutar"),
            bg="#0d9488",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=self.ejecutar_consulta,
        ).pack(side="right")

        # Botonera de Consultas Rápidas Preconfiguradas (Presets)
        fila_presets = tk.Frame(self.master, bg="#060911")
        fila_presets.pack(fill="x", padx=14, pady=(4, 8))

        tk.Label(
            fila_presets, text=t("sql_presets"), bg="#060911", fg="#94a3b8", font=("Segoe UI", 8, "bold")
        ).pack(side="left", padx=(0, 6))

        presets = [
            (
                "👨‍🚀 Vista Tripulación Activa",
                "SELECT codigo_astronauta, nombres, apellidos, rol, especialidad, racha_autocuidado FROM vista_tripulacion_activa",
            ),
            (
                "🚨 Lecturas Críticas",
                "SELECT id, fecha, id_tripulante, presion_sistolica, frecuencia_cardiaca, glucosa_mg_dl, sistema_afectado FROM lecturas_biometricas WHERE nivel_alerta = 'CRITICO' ORDER BY id DESC",
            ),
            (
                "📦 Stock Botiquín 3FN",
                "SELECT codigo, nombre, sistema_corporal, stock_actual, stock_minimo, unidad_medida FROM insumos_medicos",
            ),
            (
                "📊 Promedios por Alerta",
                "SELECT nivel_alerta, COUNT(*) AS total, ROUND(AVG(presion_media),1) AS map_prom, ROUND(AVG(glucosa_mg_dl),1) AS glu_prom FROM lecturas_biometricas GROUP BY nivel_alerta",
            ),
        ]

        for etiqueta_p, sql_p in presets:
            tk.Button(
                fila_presets,
                text=etiqueta_p,
                bg="#1e293b",
                fg="#38bdf8",
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=3,
                command=lambda q=sql_p: self._cargar_y_ejecutar_preset(q),
            ).pack(side="left", padx=3)

        # Tabla de Resultados con Scrollbar
        marco_tabla = tk.Frame(self.master, bg="#10182a")
        marco_tabla.pack(fill="both", expand=True, padx=14, pady=(2, 6))

        scroll_y = ttk.Scrollbar(marco_tabla, orient="vertical")
        self.tabla = ttk.Treeview(marco_tabla, show="headings", height=14, yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tabla.yview)

        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Barra de estado inferior
        self.lbl_estado = tk.Label(
            self.master,
            text="",
            bg="#060911",
            fg="#4CAF50",
            font=("Segoe UI", 8, "bold"),
        )
        self.lbl_estado.pack(anchor="w", padx=14, pady=(0, 8))

    def _cargar_y_ejecutar_preset(self, query: str) -> None:
        self.txt_query.delete(0, tk.END)
        self.txt_query.insert(0, query)
        self.ejecutar_consulta()

    def ejecutar_consulta(self) -> bool:
        query = self.txt_query.get().strip()
        try:
            res = self.api.ejecutar_sql_sandbox(query)
            columnas = res.get("columnas", [])
            filas = res.get("filas", [])

            self.tabla.delete(*self.tabla.get_children())
            self.tabla["columns"] = columnas
            for c in columnas:
                self.tabla.heading(c, text=c)
                self.tabla.column(c, width=125, anchor="center")

            for f in filas:
                self.tabla.insert("", "end", values=[f.get(c) for c in columnas])

            self.lbl_estado.configure(text=t("sql_estado_ok", filas=len(filas)))
            return True
        except ErrorClienteAPI as e:
            messagebox.showerror(t("sql_err_titulo"), str(e))
            return False