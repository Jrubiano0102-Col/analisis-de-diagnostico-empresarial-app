"""
main_window.py
Ventana principal de inicio para Diagnóstico Empresarial Multidimensional.
Soporte completo y universal para Excel (.xlsx, .xls) y CSV.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Any, Dict, List
import pandas as pd

from app.ui.styles import PALETTE, FONTS
from app.core.data_loader import DataLoader
from app.core.analyzer import BusinessAnalyzer
from app.ui.dashboard_view import DashboardView
from app.ui.components.mapping_dialog import ColumnMappingDialog


class ModernButton(tk.Canvas):
    """Botón personalizado con esquinas redondeadas y efectos hover."""
    def __init__(self, parent, text: str, bg_color: str, hover_color: str,
                 text_color: str = "#FFFFFF", command=None, width: int = 150, height: int = 40):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.text = text
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.command = command
        self.width = width
        self.height = height
        self._enabled = True

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

        self._draw(self.bg_color)

    def _draw(self, color: str):
        self.delete("all")
        radius = 8
        w, h = self.width, self.height
        
        # Rectángulo redondeado
        self.create_arc((0, 0, radius * 2, radius * 2), start=90, extent=90, fill=color, outline=color)
        self.create_arc((w - radius * 2, 0, w, radius * 2), start=0, extent=90, fill=color, outline=color)
        self.create_arc((0, h - radius * 2, radius * 2, h), start=180, extent=90, fill=color, outline=color)
        self.create_arc((w - radius * 2, h - radius * 2, w, h), start=270, extent=90, fill=color, outline=color)
        self.create_rectangle((radius, 0, w - radius, h), fill=color, outline=color)
        self.create_rectangle((0, radius, w, h - radius), fill=color, outline=color)

        self.create_text(w / 2, h / 2, text=self.text, fill=self.text_color, font=FONTS["btn"])

    def _on_enter(self, _):
        if self._enabled:
            self._draw(self.hover_color)
            self.config(cursor="hand2")

    def _on_leave(self, _):
        if self._enabled:
            self._draw(self.bg_color)
            self.config(cursor="")

    def _on_click(self, _):
        if self._enabled and self.command:
            self.command()

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        if enabled:
            self._draw(self.bg_color)
        else:
            self._draw("#CBD5E1")


class MainWindow(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()

        self.title("DIAGNÓSTICO EMPRESARIAL - Plataforma Multidimensional")
        self.geometry("1080x690")
        self.minsize(800, 480)
        self.configure(bg=PALETTE["bg_main"])

        # Estado interno
        self.current_file_path: Optional[str] = None
        self.current_data: Optional[Any] = None
        self.current_metadata: Dict[str, Any] = {}
        self.analyzer: Optional[BusinessAnalyzer] = None
        self.dashboard_view: Optional[DashboardView] = None

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        """Configuración de estilos ttk."""
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Custom.Treeview",
            background="#FFFFFF",
            foreground=PALETTE["text_primary"],
            rowheight=26,
            fieldbackground="#FFFFFF",
            font=FONTS["body"],
            borderwidth=0,
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#F1F5F9",
            foreground=PALETTE["text_primary"],
            font=FONTS["body_bold"],
            borderwidth=1,
            relief="flat",
        )
        style.map("Custom.Treeview", background=[("selected", "#DBEAFE")], foreground=[("selected", "#1E3A8A")])

    def _build_ui(self):
        """Construye todos los componentes de la interfaz de inicio."""
        self._build_header()
        self._build_action_bar()
        self._build_info_card()
        self._build_content_area()
        self._build_status_bar()

    def _build_header(self):
        header_frame = tk.Frame(self, bg=PALETTE["bg_header"], height=70)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        container = tk.Frame(header_frame, bg=PALETTE["bg_header"])
        container.pack(fill=tk.BOTH, expand=True, padx=18, pady=8)

        title_label = tk.Label(
            container,
            text="DIAGNÓSTICO EMPRESARIAL",
            font=("Segoe UI", 16, "bold"),
            fg=PALETTE["text_header"],
            bg=PALETTE["bg_header"],
            anchor="w"
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            container,
            text="Sistema de Evaluación Multidimensional • KPIs • Análisis Causal de Problemas • Excel y CSV",
            font=("Segoe UI", 10, "normal"),
            fg="#94A3B8",
            bg=PALETTE["bg_header"],
            anchor="w"
        )
        subtitle_label.pack(anchor="w", pady=(1, 0))

    def _build_action_bar(self):
        """Barra con los tres botones requeridos más opción de mapeo y borrado."""
        action_card = tk.Frame(self, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"])
        action_card.pack(fill=tk.X, padx=14, pady=(8, 6))

        inner = tk.Frame(action_card, bg=PALETTE["bg_card"], padx=14, pady=8)
        inner.pack(fill=tk.X)

        # Botón 1: Cargar Archivo
        self.btn_load = ModernButton(
            inner,
            text="📂 Cargar Archivo",
            bg_color=PALETTE["btn_load"],
            hover_color=PALETTE["btn_load_hover"],
            command=self.on_load_file,
            width=160,
            height=42
        )
        self.btn_load.pack(side=tk.LEFT, padx=(0, 10))

        # Botón 2: Analizar
        self.btn_analyze = ModernButton(
            inner,
            text="📊 Analizar",
            bg_color=PALETTE["btn_analyze"],
            hover_color=PALETTE["btn_analyze_hover"],
            command=self.on_analyze,
            width=140,
            height=42
        )
        self.btn_analyze.pack(side=tk.LEFT, padx=(0, 10))
        self.btn_analyze.set_enabled(False)

        # Botón Asistente: Mapear Columnas (Aparece cuando hay archivo cargado)
        self.btn_map_cols = tk.Button(
            inner,
            text="⚙️ Mapear Columnas",
            font=("Segoe UI", 10, "bold"),
            bg="#F1F5F9",
            fg=PALETTE["text_primary"],
            relief="solid",
            bd=1,
            padx=12,
            pady=8,
            cursor="hand2",
            state=tk.DISABLED,
            command=self.open_column_mapping_dialog
        )
        self.btn_map_cols.pack(side=tk.LEFT, padx=(0, 10))

        # Botón 3: Borrar
        self.btn_delete = ModernButton(
            inner,
            text="🗑️ Borrar",
            bg_color=PALETTE["btn_delete"],
            hover_color=PALETTE["btn_delete_hover"],
            command=self.on_delete,
            width=130,
            height=42
        )
        self.btn_delete.pack(side=tk.LEFT)
        self.btn_delete.set_enabled(False)

        # Etiqueta de ayuda rápida a la derecha
        self.quick_hint = tk.Label(
            inner,
            text="Formatos: Excel (.xlsx, .xls) y CSV",
            font=FONTS["caption"],
            fg=PALETTE["text_muted"],
            bg=PALETTE["bg_card"]
        )
        self.quick_hint.pack(side=tk.RIGHT, pady=10)

    def _build_info_card(self):
        """Tarjeta resumen de detalles del archivo cargado."""
        self.info_card = tk.Frame(self, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"])
        self.info_card.pack(fill=tk.X, padx=14, pady=(0, 6))

        inner = tk.Frame(self.info_card, bg=PALETTE["bg_card"], padx=14, pady=6)
        inner.pack(fill=tk.X)

        self.lbl_file_name = tk.Label(
            inner,
            text="Archivo: Ningún archivo seleccionado",
            font=FONTS["body_bold"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"]
        )
        self.lbl_file_name.pack(side=tk.LEFT)

        self.lbl_file_stats = tk.Label(
            inner,
            text="• Filas: 0  • Columnas: 0  • Tamaño: 0 KB",
            font=FONTS["body"],
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_card"]
        )
        self.lbl_file_stats.pack(side=tk.LEFT, padx=10)

        # Selector de hoja si el Excel tiene múltiples hojas
        self.sheet_selector_frame = tk.Frame(inner, bg=PALETTE["bg_card"])
        self.sheet_selector_frame.pack(side=tk.LEFT, padx=6)

        # Pill de Estado
        self.lbl_badge = tk.Label(
            inner,
            text="SIN ARCHIVO",
            font=("Segoe UI", 8, "bold"),
            fg="#64748B",
            bg="#F1F5F9",
            padx=8,
            pady=2
        )
        self.lbl_badge.pack(side=tk.RIGHT)

    def _build_content_area(self):
        """Área central dinámica."""
        self.content_container = tk.Frame(self, bg=PALETTE["bg_main"])
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 6))

        # 1. Vista vacía
        self.empty_view = tk.Frame(
            self.content_container,
            bg=PALETTE["bg_card"],
            bd=1,
            relief="solid",
            highlightbackground=PALETTE["border"]
        )
        self.empty_view.pack(fill=tk.BOTH, expand=True)

        empty_inner = tk.Frame(self.empty_view, bg=PALETTE["bg_card"], padx=30, pady=30)
        empty_inner.place(relx=0.5, rely=0.5, anchor="center")

        icon_label = tk.Label(
            empty_inner,
            text="📂",
            font=("Segoe UI", 48),
            bg=PALETTE["bg_card"],
            fg="#94A3B8"
        )
        icon_label.pack()

        welcome_label = tk.Label(
            empty_inner,
            text="Cargue los datos de su empresa para iniciar el diagnóstico",
            font=FONTS["section_title"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"]
        )
        welcome_label.pack(pady=(10, 5))

        desc_label = tk.Label(
            empty_inner,
            text="Haga clic en 'Cargar Archivo' y seleccione su archivo Excel (.xlsx, .xls) o CSV.\n"
                 "El sistema evaluará indicadores en dimensiones Financiera, Operativa, Comercial y Talento Humano.",
            font=FONTS["body"],
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_card"],
            justify="center"
        )
        desc_label.pack(pady=(0, 20))

        dims_frame = tk.Frame(empty_inner, bg=PALETTE["bg_card"])
        dims_frame.pack()

        dim_boxes = [
            ("💰 Financiera", "Rentabilidad, Costos, Márgenes"),
            ("📈 Comercial", "Ventas, Conversión, Clientes"),
            ("⚙️ Operativa", "Productividad, Eficiencia, Inventarios"),
            ("👥 Talento", "Desempeño, Retención, Clima"),
        ]

        for title, sub in dim_boxes:
            box = tk.Frame(dims_frame, bg="#F8FAFC", bd=1, relief="solid", highlightbackground="#E2E8F0", padx=12, pady=8)
            box.pack(side=tk.LEFT, padx=6)
            tk.Label(box, text=title, font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg="#F8FAFC").pack(anchor="w")
            tk.Label(box, text=sub, font=FONTS["caption"], fg=PALETTE["text_muted"], bg="#F8FAFC").pack(anchor="w")

        # 2. Vista previa con tabla de datos cargados
        self.data_view = tk.Frame(self.content_container, bg=PALETTE["bg_card"])

        self.table_header = tk.Frame(self.data_view, bg=PALETTE["bg_card"], pady=8, padx=12)
        self.table_header.pack(fill=tk.X)

        self.lbl_table_title = tk.Label(
            self.table_header,
            text="Vista Previa de Datos Cargados",
            font=FONTS["section_title"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"]
        )
        self.lbl_table_title.pack(side=tk.LEFT)

        # Botón rápido para configurar mapeo desde la vista previa
        btn_quick_map = tk.Button(
            self.table_header,
            text="⚙️ Verificar Columnas",
            font=("Segoe UI", 9),
            bg="#F1F5F9",
            fg=PALETTE["text_primary"],
            relief="solid",
            bd=1,
            padx=10,
            pady=2,
            cursor="hand2",
            command=self.open_column_mapping_dialog
        )
        btn_quick_map.pack(side=tk.RIGHT)

        tree_container = tk.Frame(self.data_view, bg=PALETTE["bg_card"])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self.scroll_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL)
        self.scroll_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            tree_container,
            style="Custom.Treeview",
            yscrollcommand=self.scroll_y.set,
            xscrollcommand=self.scroll_x.set
        )
        self.scroll_y.config(command=self.tree.yview)
        self.scroll_x.config(command=self.tree.xview)

        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _build_status_bar(self):
        """Barra de estado inferior."""
        self.status_bar = tk.Frame(self, bg="#FFFFFF", bd=1, relief="solid", highlightbackground=PALETTE["border"], height=30)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        self.lbl_status = tk.Label(
            self.status_bar,
            text="Listo. Seleccione un archivo Excel (.xlsx, .xls) o CSV para comenzar.",
            font=FONTS["caption"],
            fg=PALETTE["text_secondary"],
            bg="#FFFFFF",
            padx=15
        )
        self.lbl_status.pack(side=tk.LEFT, fill=tk.Y)

    # ==========================================================
    # CONTROLADORES DE EVENTOS DE LOS BOTONES
    # ==========================================================

    def on_load_file(self):
        """Acción del botón 'Cargar Archivo'."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de datos empresariales",
            filetypes=[
                ("Archivos soportados (Excel y CSV)", "*.xlsx *.xls *.csv *.xlsm"),
                ("Archivos Excel (*.xlsx, *.xls)", "*.xlsx *.xls *.xlsm"),
                ("Archivos CSV (*.csv)", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not file_path:
            return

        self._load_file_data(file_path)

    def _load_file_data(self, file_path: str, sheet_name: Optional[str] = None):
        """Carga y procesa el archivo indicado."""
        self.lbl_status.config(text="Cargando y procesando archivo...")
        self.update_idletasks()

        success, msg, data, metadata = DataLoader.load_file(file_path, sheet_name=sheet_name)

        if not success:
            messagebox.showerror("Error al cargar archivo", msg)
            self.lbl_status.config(text=f"Error: {msg}")
            return

        if self.dashboard_view:
            self.dashboard_view.destroy()
            self.dashboard_view = None

        self.current_file_path = file_path
        self.current_data = data
        self.current_metadata = metadata
        self.analyzer = BusinessAnalyzer(data=data, metadata=metadata)

        # Actualizar información
        sheet_text = f" [Hoja: '{metadata['sheet_name']}']" if metadata.get("sheet_name") else ""
        self.lbl_file_name.config(text=f"Archivo: {metadata['file_name']}{sheet_text}")
        self.lbl_file_stats.config(
            text=f"• Filas: {metadata['rows']:,}  • Columnas: {metadata['cols']}  • Tamaño: {metadata['file_size_kb']} KB"
        )
        self.lbl_badge.config(text="ARCHIVO CARGADO", fg="#047857", bg="#D1FAE5")

        # Configurar selector de hojas si hay más de 1
        for w in self.sheet_selector_frame.winfo_children():
            w.destroy()

        sheets = metadata.get("available_sheets", [])
        if len(sheets) > 1:
            tk.Label(self.sheet_selector_frame, text="Hoja:", font=FONTS["caption"], bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"]).pack(side=tk.LEFT)
            sheet_var = tk.StringVar(value=metadata.get("sheet_name", sheets[0]))
            cb_sheets = ttk.Combobox(self.sheet_selector_frame, textvariable=sheet_var, values=sheets, state="readonly", width=14, font=("Segoe UI", 8))
            cb_sheets.pack(side=tk.LEFT, padx=4)
            cb_sheets.bind("<<ComboboxSelected>>", lambda e: self._load_file_data(file_path, sheet_name=sheet_var.get()))

        # Habilitar botones Analizar, Mapear y Borrar
        self.btn_analyze.set_enabled(True)
        self.btn_delete.set_enabled(True)
        self.btn_map_cols.config(state=tk.NORMAL)

        # Mostrar tabla de vista previa
        self._populate_preview_table(self.tree)
        self.empty_view.pack_forget()
        self.data_view.pack(fill=tk.BOTH, expand=True)

        self.lbl_status.config(text=f"{msg} Haga clic en 'Analizar' para ver el diagnóstico multidimensional.")

    def _populate_preview_table(self, target_tree):
        """Rellena un Treeview con la muestra de filas formateadas."""
        target_tree.delete(*target_tree.get_children())
        target_tree["columns"] = []

        cols = self.current_metadata.get("columns", [])
        if not cols:
            return

        target_tree["columns"] = cols
        target_tree["show"] = "headings"

        for col in cols:
            target_tree.heading(col, text=col)
            col_width = max(len(str(col)) * 11, 105)
            target_tree.column(col, width=min(col_width, 240), anchor="center")

        if hasattr(self.current_data, "head"):
            sample_df = self.current_data.head(150)
            for _, row in sample_df.iterrows():
                vals = []
                for val in row.values:
                    if pd.isnull(val):
                        vals.append("")
                    elif hasattr(val, "strftime"):
                        vals.append(val.strftime("%Y-%m-%d"))
                    elif isinstance(val, float):
                        vals.append(f"{val:,.2f}" if abs(val) >= 1000 else f"{val:.2f}")
                    else:
                        vals.append(str(val))
                target_tree.insert("", tk.END, values=vals)
        elif isinstance(self.current_data, list):
            for row in self.current_data[:150]:
                target_tree.insert("", tk.END, values=row)

    def _build_embedded_table(self, parent_frame):
        """Construye una tabla embebida para la pestaña de datos del Dashboard."""
        header = tk.Frame(parent_frame, bg=PALETTE["bg_card"], pady=8, padx=12)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="Explorador de Datos del Archivo",
            font=FONTS["section_title"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"]
        ).pack(side=tk.LEFT)

        btn_map = tk.Button(
            header,
            text="⚙️ Reasignar Columnas",
            font=("Segoe UI", 9),
            bg="#F1F5F9",
            fg=PALETTE["text_primary"],
            relief="solid",
            bd=1,
            padx=10,
            pady=2,
            cursor="hand2",
            command=self.open_column_mapping_dialog
        )
        btn_map.pack(side=tk.RIGHT)

        container = tk.Frame(parent_frame, bg=PALETTE["bg_card"])
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        sc_y = ttk.Scrollbar(container, orient=tk.VERTICAL)
        sc_x = ttk.Scrollbar(container, orient=tk.HORIZONTAL)

        embedded_tree = ttk.Treeview(
            container,
            style="Custom.Treeview",
            yscrollcommand=sc_y.set,
            xscrollcommand=sc_x.set
        )
        sc_y.config(command=embedded_tree.yview)
        sc_x.config(command=embedded_tree.xview)

        sc_y.pack(side=tk.RIGHT, fill=tk.Y)
        sc_x.pack(side=tk.BOTTOM, fill=tk.X)
        embedded_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._populate_preview_table(embedded_tree)

    def open_column_mapping_dialog(self):
        """Abre el diálogo para que el usuario verifique o asigne columnas manualmente."""
        if not self.analyzer or self.current_data is None:
            messagebox.showwarning("Atención", "Primero debe cargar un archivo Excel o CSV.")
            return

        def _on_confirm(new_map):
            self.analyzer.set_custom_mapping(new_map)
            self.lbl_status.config(text="Columnas reasignadas correctamente.")
            self.on_analyze()

        cols = self.current_metadata.get("columns", [])
        ColumnMappingDialog(
            self,
            available_columns=cols,
            current_mapping=self.analyzer.col_map,
            on_confirm_callback=_on_confirm
        )

    def on_analyze(self):
        """Acción del botón 'Analizar': Despliega el Panel de Resultados Multidimensional."""
        if self.current_data is None or self.analyzer is None:
            messagebox.showwarning("Atención", "Primero debe cargar un archivo Excel o CSV.")
            return

        # Si no se detectó automáticamente la columna de ventas, abrir asistente de mapeo
        if not self.analyzer.col_map.get("ventas"):
            resp = messagebox.askyesno(
                "Configuración de Columnas Necesaria",
                "El archivo Excel se cargó correctamente, pero no se pudo identificar automáticamente qué columna corresponde a 'Ventas / Ingresos'.\n\n"
                "¿Desea seleccionarla ahora para que la aplicación pueda calcular todos los indicadores y gráficas?"
            )
            if resp:
                self.open_column_mapping_dialog()
            return

        self.lbl_status.config(text="Calculando KPIs y detectando problemas multidimensionales...")
        self.lbl_badge.config(text="ANALIZANDO...", fg="#1E40AF", bg="#DBEAFE")
        self.update_idletasks()

        results = self.analyzer.run_full_diagnosis()

        self.empty_view.pack_forget()
        self.data_view.pack_forget()

        if self.dashboard_view:
            self.dashboard_view.destroy()

        self.dashboard_view = DashboardView(
            self.content_container,
            analysis_results=results,
            df=self.analyzer.df,
            table_widget_builder=self._build_embedded_table
        )
        self.dashboard_view.pack(fill=tk.BOTH, expand=True)

        self.lbl_badge.config(text="DIAGNÓSTICO COMPLETADO", fg="#065F46", bg="#A7F3D0")
        prob_count = len(results.get("problems", []))
        self.lbl_status.config(
            text=f"Análisis completado: {prob_count} hallazgos/situaciones de atención identificadas. Revise las pestañas de KPIs, Gráficas y Problemas."
        )

    def on_delete(self):
        """Acción del botón 'Borrar'."""
        if self.current_data is not None:
            confirm = messagebox.askyesno(
                "Confirmar borrado",
                "¿Está seguro de que desea borrar los datos cargados y reiniciar el diagnóstico?"
            )
            if not confirm:
                return

        if self.dashboard_view:
            self.dashboard_view.destroy()
            self.dashboard_view = None

        self.current_file_path = None
        self.current_data = None
        self.current_metadata = {}
        self.analyzer = None

        self.lbl_file_name.config(text="Archivo: Ningún archivo seleccionado")
        self.lbl_file_stats.config(text="• Filas: 0  • Columnas: 0  • Tamaño: 0 KB")
        self.lbl_badge.config(text="SIN ARCHIVO", fg="#64748B", bg="#F1F5F9")

        for w in self.sheet_selector_frame.winfo_children():
            w.destroy()

        self.btn_analyze.set_enabled(False)
        self.btn_delete.set_enabled(False)
        self.btn_map_cols.config(state=tk.DISABLED)

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []
        self.data_view.pack_forget()
        self.empty_view.pack(fill=tk.BOTH, expand=True)

        self.lbl_status.config(text="Datos y análisis borrados correctamente. Puede cargar un nuevo archivo.")
