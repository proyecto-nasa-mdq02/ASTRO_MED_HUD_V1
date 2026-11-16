# =======================================================================
#  NODO DE ARRANQUE Y BOOTSTRAP LAN — CONSOLA DE COMANDO MÉDICO (CAPA 4)
# =======================================================================

import atexit
import functools
import socket
import threading
import time
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import uvicorn

from simulador_misiones.generador_mision_artemis import inicializar_y_poblar_mision
from src.infraestructura.api.servidor import app
from src.presentacion.i18n import set_idioma, t
from src.presentacion.consola_comando.cliente_api import ClienteAPIAstroMed, ErrorClienteAPI
from src.presentacion.consola_comando.vistas.panel_control import VentanaPanelControl

_SERVIDOR_WEB_HTTP = None


def aplicar_tema_aeroespacial(widget_raiz: tk.Misc) -> None:
    """Configura el tema oscuro táctico ('clam') para Treeview, Combobox y Scrollbars."""
    estilo = ttk.Style(widget_raiz)
    try:
        estilo.theme_use("clam")
    except Exception:
        pass

    estilo.configure(
        "Treeview",
        background="#0f172a",
        foreground="#e2e8f0",
        fieldbackground="#0f172a",
        borderwidth=0,
        rowheight=27,
        font=("Segoe UI", 9),
    )
    estilo.configure(
        "Treeview.Heading",
        background="#1e293b",
        foreground="#38bdf8",
        relief="flat",
        font=("Segoe UI", 9, "bold"),
        padding=(6, 5),
    )
    estilo.map(
        "Treeview",
        background=[("selected", "#0284c7")],
        foreground=[("selected", "#ffffff")],
    )
    estilo.map(
        "Treeview.Heading",
        background=[("active", "#334155")],
    )
    estilo.configure(
        "TCombobox",
        fieldbackground="#0f172a",
        background="#1e293b",
        foreground="#f8fafc",
        arrowcolor="#38bdf8",
    )


def obtener_ip_lan() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def iniciar_demonios_red() -> None:
    """Inicializa la base de datos de misión y levanta API REST (8000) + HUD Web (8080)."""
    global _SERVIDOR_WEB_HTTP
    inicializar_y_poblar_mision("db/astro_med.db")

    def correr_api():
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
        server = uvicorn.Server(config)
        server.run()

    hilo_api = threading.Thread(target=correr_api, daemon=True)
    hilo_api.start()

    ruta_hud = Path(__file__).resolve().parent.parent.parent / "hud_astronauta"
    manejador = functools.partial(SimpleHTTPRequestHandler, directory=str(ruta_hud))

    try:
        _SERVIDOR_WEB_HTTP = HTTPServer(("0.0.0.0", 8080), manejador)
        hilo_web = threading.Thread(target=_SERVIDOR_WEB_HTTP.serve_forever, daemon=True)
        hilo_web.start()
    except OSError:
        pass

    atexit.register(apagar_demonios)
    time.sleep(0.6)


def apagar_demonios() -> None:
    global _SERVIDOR_WEB_HTTP
    if _SERVIDOR_WEB_HTTP:
        try:
            _SERVIDOR_WEB_HTTP.shutdown()
        except Exception:
            pass


class VentanaLogin:
    def __init__(self, root: tk.Tk, cliente_api: ClienteAPIAstroMed):
        self.root = root
        self.api = cliente_api
        self.ip_lan = obtener_ip_lan()

        aplicar_tema_aeroespacial(self.root)
        self.root.title("ASTRO-MED HUD | NASA HRP Flight Control")
        self.root.geometry("540x540")
        self.root.configure(bg="#060911")

        marco = tk.Frame(
            self.root,
            bg="#10182a",
            padx=30,
            pady=24,
            highlightbackground="#38bdf8",
            highlightthickness=1,
        )
        marco.pack(expand=True, fill="both", padx=24, pady=22)

        # Barra superior con selector de idioma
        fila_idioma = tk.Frame(marco, bg="#10182a")
        fila_idioma.pack(fill="x", pady=(0, 12))

        self.lbl_idioma = tk.Label(
            fila_idioma, text=t("login_idioma"), fg="#94a3b8", bg="#10182a", font=("Segoe UI", 9, "bold")
        )
        self.lbl_idioma.pack(side="left")

        self.combo_idioma = ttk.Combobox(
            fila_idioma, values=["Español (ES)", "English (EN)"], state="readonly", width=16
        )
        self.combo_idioma.current(0)
        self.combo_idioma.pack(side="right")
        self.combo_idioma.bind("<<ComboboxSelected>>", self.cambiar_idioma_ui)

        # Encabezado de Misión
        self.lbl_sub = tk.Label(
            marco, text=t("login_sub"), fg="#38bdf8", bg="#10182a", font=("Segoe UI", 8, "bold")
        )
        self.lbl_sub.pack(anchor="w")

        self.lbl_titulo = tk.Label(
            marco, text=t("login_titulo"), fg="#f8fafc", bg="#10182a", font=("Segoe UI", 16, "bold")
        )
        self.lbl_titulo.pack(anchor="w", pady=(2, 10))

        # Tarjeta de estado de Telemetría LAN
        panel_red = tk.Frame(marco, bg="#090d18", padx=12, pady=10, highlightbackground="#1e293b", highlightthickness=1)
        panel_red.pack(fill="x", pady=(0, 16))

        self.lbl_lan = tk.Label(
            panel_red,
            text=f"{t('login_lan')} http://{self.ip_lan}:8080",
            fg="#4CAF50",
            bg="#090d18",
            font=("Segoe UI", 9, "bold"),
        )
        self.lbl_lan.pack(anchor="w")

        self.lbl_api = tk.Label(
            panel_red,
            text=t("login_api_status"),
            fg="#94a3b8",
            bg="#090d18",
            font=("Segoe UI", 8),
        )
        self.lbl_api.pack(anchor="w", pady=(2, 0))

        # Campos de acceso de Control de Vuelo
        self.lbl_usr = tk.Label(
            marco, text=t("login_usuario"), fg="#cbd5e1", bg="#10182a", font=("Segoe UI", 9, "bold")
        )
        self.lbl_usr.pack(anchor="w")
        self.ent_usuario = tk.Entry(
            marco,
            font=("Segoe UI", 11),
            bg="#090d18",
            fg="#ffffff",
            insertbackground="#38bdf8",
            relief="flat",
            highlightbackground="#334155",
            highlightcolor="#38bdf8",
            highlightthickness=1,
        )
        self.ent_usuario.insert(0, "admin")
        self.ent_usuario.pack(fill="x", pady=(4, 12), ipady=5)

        self.lbl_pwd = tk.Label(
            marco, text=t("login_clave"), fg="#cbd5e1", bg="#10182a", font=("Segoe UI", 9, "bold")
        )
        self.lbl_pwd.pack(anchor="w")
        self.ent_password = tk.Entry(
            marco,
            show="*",
            font=("Segoe UI", 11),
            bg="#090d18",
            fg="#ffffff",
            insertbackground="#38bdf8",
            relief="flat",
            highlightbackground="#334155",
            highlightcolor="#38bdf8",
            highlightthickness=1,
        )
        self.ent_password.insert(0, "admin123")
        self.ent_password.pack(fill="x", pady=(4, 18), ipady=5)

        self.btn_ingresar = tk.Button(
            marco,
            text=t("login_btn_iniciar"),
            bg="#0284c7",
            activebackground="#0369a1",
            activeforeground="white",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            pady=9,
            command=self.autenticar,
        )
        self.btn_ingresar.pack(fill="x", pady=(0, 8))

        self.btn_hud = tk.Button(
            marco,
            text=t("login_btn_hud"),
            bg="#0d9488",
            activebackground="#0f766e",
            activeforeground="white",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            pady=7,
            command=lambda: webbrowser.open("http://127.0.0.1:8080"),
        )
        self.btn_hud.pack(fill="x")

    def cambiar_idioma_ui(self, _evento=None) -> None:
        seleccion = self.combo_idioma.get()
        cod = "en" if "EN" in seleccion else "es"
        set_idioma(cod)
        self.api.cambiar_idioma(cod)

        self.lbl_idioma.configure(text=t("login_idioma"))
        self.lbl_sub.configure(text=t("login_sub"))
        self.lbl_titulo.configure(text=t("login_titulo"))
        self.lbl_lan.configure(text=f"{t('login_lan')} http://{self.ip_lan}:8080")
        self.lbl_api.configure(text=t("login_api_status"))
        self.lbl_usr.configure(text=t("login_usuario"))
        self.lbl_pwd.configure(text=t("login_clave"))
        self.btn_ingresar.configure(text=t("login_btn_iniciar"))
        self.btn_hud.configure(text=t("login_btn_hud"))

    def autenticar(self) -> bool:
        usuario = self.ent_usuario.get().strip()
        password = self.ent_password.get().strip()
        try:
            datos = self.api.login(usuario, password)
            messagebox.showinfo(
                t("login_ok_titulo"),
                t("login_ok_msg", nombre=f"{datos['nombres']} {datos['apellidos']}", rol=datos["rol"]),
            )
            self.abrir_panel_control()
            return True
        except ErrorClienteAPI as e:
            messagebox.showerror(t("login_err_titulo"), str(e))
            return False

    def abrir_panel_control(self) -> None:
        top = tk.Toplevel(self.root)
        self.root.withdraw()
        VentanaPanelControl(top, self.api, al_cerrar=self.root.deiconify)


if __name__ == "__main__":
    iniciar_demonios_red()
    raiz = tk.Tk()
    cliente = ClienteAPIAstroMed("http://127.0.0.1:8000/api")
    app_login = VentanaLogin(raiz, cliente)
    raiz.mainloop()