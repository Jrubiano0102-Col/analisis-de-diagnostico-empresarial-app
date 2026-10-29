"""
dashboard_view.py
Contenedor principal del Panel de Resultados del Diagnóstico Empresarial.
Completamente adaptable y con scroll interactivo para modo ventana y pantalla completa.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any

from app.ui.styles import PALETTE, FONTS
from app.ui.components.kpi_card import KPICard
from app.ui.components.charts_view import ChartsView
from app.ui.components.problems_view import ProblemsView


class DashboardView(tk.Frame):
    """Panel de Resultados con navegación por pestañas y visualización multidimensional."""

    def __init__(self, parent, analysis_results: Dict[str, Any], df, table_widget_builder, **kwargs):
        super().__init__(parent, bg=PALETTE["bg_main"], **kwargs)
        self.results = analysis_results
        self.df = df
        self.table_builder = table_widget_builder
        self.current_tab = "kpis"

        self._build_ui()

    def _build_ui(self):
        # 1. BARRA SUPERIOR DE SALUD GENERAL
        self._build_dimension_health_bar()

        # 2. BARRA DE NAVEGACIÓN ENTRE PESTAÑAS
        self._build_tab_bar()

        # 3. CONTENEDOR CENTRAL DE PESTAÑAS
        self.tab_container = tk.Frame(self, bg=PALETTE["bg_main"])
        self.tab_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 6))

        self.views = {}
        self._init_kpis_view()
        self._init_charts_view()
        self._init_problems_view()
        self._init_data_table_view()

        # Enlazar rueda del ratón de forma universal e ininterrumpida
        self._bind_global_mousewheel()

        self._switch_tab("kpis")

    def _bind_global_mousewheel(self):
        """Distribuidor global de eventos de rueda del ratón según la pestaña activa."""
        def _dispatcher(event):
            delta = event.delta
            if self.current_tab == "problems" and "problems" in self.views:
                self.views["problems"].scroll_canvas(delta)
            elif self.current_tab == "kpis" and hasattr(self, "kpi_canvas"):
                try:
                    self.kpi_canvas.yview_scroll(int(-1 * (delta / 120)), "units")
                except Exception:
                    pass
            elif self.current_tab == "charts" and "charts" in self.views and hasattr(self.views["charts"], "scroll_canvas"):
                self.views["charts"].scroll_canvas(delta)

        self.bind_all("<MouseWheel>", _dispatcher)

    def _build_dimension_health_bar(self):
        """Barra resumen del estado general de cada una de las 4 dimensiones."""
        dims_card = tk.Frame(self, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"], padx=14, pady=8)
        dims_card.pack(fill=tk.X, padx=12, pady=(6, 6))

        tk.Label(
            dims_card,
            text="Salud Empresarial:",
            font=FONTS["body_bold"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"]
        ).pack(side=tk.LEFT, padx=(0, 8))

        dims_summary = self.results.get("dimensions_summary", {})
        icons = {
            "financiera": "💰",
            "comercial": "📈",
            "operativa": "⚙️",
            "talento": "👥"
        }

        chips_frame = tk.Frame(dims_card, bg=PALETTE["bg_card"])
        chips_frame.pack(side=tk.LEFT)

        for key, info in dims_summary.items():
            icon = icons.get(key, "●")
            chip = tk.Frame(chips_frame, bg="#F8FAFC", bd=1, relief="solid", highlightbackground="#E2E8F0", padx=7, pady=2)
            chip.pack(side=tk.LEFT, padx=3)

            tk.Label(
                chip,
                text=f"{icon} {info['name']}:",
                font=("Segoe UI", 8, "bold"),
                fg=PALETTE["text_primary"],
                bg="#F8FAFC"
            ).pack(side=tk.LEFT)

            tk.Label(
                chip,
                text=f" {info['status']}",
                font=("Segoe UI", 8, "bold"),
                fg=info["color"],
                bg="#F8FAFC"
            ).pack(side=tk.LEFT)

        btn_export = tk.Button(
            dims_card,
            text="📥 Exportar Informe",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg=PALETTE["text_primary"],
            relief="solid",
            bd=1,
            padx=10,
            pady=2,
            cursor="hand2",
            command=self._export_report
        )
        btn_export.pack(side=tk.RIGHT)

    def _build_tab_bar(self):
        """Barra de navegación tipo pills."""
        bar = tk.Frame(self, bg=PALETTE["bg_main"], padx=12)
        bar.pack(fill=tk.X, pady=(0, 6))

        self.tab_buttons = {}
        tabs = [
            ("kpis", "📊 Indicadores Clave & KPIs"),
            ("charts", "📈 Gráficas y Tendencias"),
            ("problems", f"🚨 Situaciones de Atención ({len(self.results.get('problems', []))})"),
            ("data", "📋 Vista de Tabla")
        ]

        for tab_id, text in tabs:
            btn = tk.Button(
                bar,
                text=text,
                font=FONTS["body_bold"],
                relief="flat",
                bd=0,
                padx=14,
                pady=6,
                cursor="hand2",
                command=lambda tid=tab_id: self._switch_tab(tid)
            )
            btn.pack(side=tk.LEFT, padx=(0, 6))
            self.tab_buttons[tab_id] = btn

    def _switch_tab(self, tab_id: str):
        self.current_tab = tab_id

        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.config(bg=PALETTE["btn_load"], fg="#FFFFFF")
            else:
                btn.config(bg="#E2E8F0", fg=PALETTE["text_primary"])

        for tid, view in self.views.items():
            if tid == tab_id:
                view.pack(fill=tk.BOTH, expand=True)
            else:
                view.pack_forget()

    def _init_kpis_view(self):
        """Construye la vista de KPIs con Canvas scrollable para que nunca se corte en modo ventana."""
        kpi_outer = tk.Frame(self.tab_container, bg=PALETTE["bg_main"])
        self.views["kpis"] = kpi_outer

        # Canvas con scroll vertical
        self.kpi_canvas = tk.Canvas(kpi_outer, bg=PALETTE["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(kpi_outer, orient="vertical", command=self.kpi_canvas.yview)
        scrollable_frame = tk.Frame(self.kpi_canvas, bg=PALETTE["bg_main"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.kpi_canvas.configure(scrollregion=self.kpi_canvas.bbox("all"))
        )

        canvas_win = self.kpi_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_canvas_configure(event):
            self.kpi_canvas.itemconfig(canvas_win, width=event.width)

        self.kpi_canvas.bind("<Configure>", _on_canvas_configure)
        self.kpi_canvas.configure(yscrollcommand=scrollbar.set)

        self.kpi_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        k = self.results.get("kpis", {})

        # 1. Valores formateados
        ingresos_val = f"${k.get('ingresos_ventas', 0):,.2f}"
        costos_val = f"${k.get('costos_operativos', 0):,.2f}"
        unidades_val = f"{k.get('unidades_vendidas', 0):,}" if k.get("unidades_vendidas") else "No especificado"

        pedidos_cnt = k.get("total_pedidos", 0)
        ticket_val = f"${k.get('ticket_promedio', 0):,.2f}" if k.get("ticket_promedio") else "N/A"
        ticket_sub = f"Base: {pedidos_cnt:,} pedidos totales" if pedidos_cnt > 0 else "Calculado sobre base comercial"

        margen_val = f"{k.get('margen_bruto_pct', 0):.2f}%"
        margen_sub = f"Utilidad bruta: ${k.get('utilidad_bruta', 0):,.2f}"

        var_pct = k.get("variacion_ventas_ultimo_pct", 0)
        signo = "+" if var_pct > 0 else ""
        var_val = f"{signo}{var_pct:.2f}%"
        var_status = "Crecimiento" if var_pct >= 0 else "Contracción"
        var_sub = f"Crecimiento global acumulado: {k.get('crecimiento_global_pct', 0):+.1f}%"

        part_list = k.get("participacion_comercial", [])
        if part_list:
            top_part = part_list[0]
            part_val = f"{top_part['participacion_pct']:.1f}% ({top_part['segmento']})"
            part_sub = f"Ventas líder: ${top_part['ventas']:,.0f} de {len(part_list)} regiones/líneas"
        else:
            part_val = "100.0%"
            part_sub = "Segmento único registrado"

        cards_data = [
            {"dim": "Ventas", "title": "• Ingresos por Ventas", "val": ingresos_val,
             "sub": f"Costos de productos: {costos_val}", "status": "Valor Total", "color": "#2563EB"},
            {"dim": "Volumen", "title": "• Unidades Vendidas", "val": unidades_val,
             "sub": "Cantidad total de productos comercializados", "status": "Productos", "color": "#0D9488"},
            {"dim": "Eficiencia Comercial", "title": "• Ticket Promedio", "val": ticket_val,
             "sub": ticket_sub, "status": "Ingresos / Pedidos", "color": "#7C3AED"},
            {"dim": "Rentabilidad", "title": "• Margen Bruto", "val": margen_val,
             "sub": margen_sub, "status": k.get("estado_margen", "Normal"),
             "color": "#EF4444" if k.get("estado_margen") == "Crítico" else "#10B981"},
            {"dim": "Evolución Temporal", "title": "• Variación de Ventas", "val": var_val,
             "sub": var_sub, "status": var_status, "color": "#10B981" if var_pct >= 0 else "#EF4444"},
            {"dim": "Distribución", "title": "• Participación Comercial", "val": part_val,
             "sub": part_sub, "status": "Cuota de Ventas", "color": "#F59E0B"},
        ]

        grid_cards = tk.Frame(scrollable_frame, bg=PALETTE["bg_main"])
        grid_cards.pack(fill=tk.X, pady=(0, 10))

        for i, cdata in enumerate(cards_data):
            r = i // 3
            c = i % 3
            card = KPICard(
                grid_cards,
                dimension=cdata["dim"],
                title=cdata["title"],
                value=cdata["val"],
                subtitle=cdata["sub"],
                status=cdata["status"],
                status_color=cdata["color"]
            )
            card.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

        grid_cards.columnconfigure(0, weight=1)
        grid_cards.columnconfigure(1, weight=1)
        grid_cards.columnconfigure(2, weight=1)

        # TABLAS DE DESGLOSE INFERIORES
        details_frame = tk.Frame(scrollable_frame, bg=PALETTE["bg_main"])
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Panel Izquierdo: Variación de Ventas
        pnl_left = tk.Frame(details_frame, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"], padx=12, pady=10)
        pnl_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        tk.Label(
            pnl_left,
            text="🔄 Variación de Ventas entre Periodos",
            font=FONTS["body_bold"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"]
        ).pack(anchor="w", pady=(0, 6))

        var_tree = ttk.Treeview(pnl_left, columns=("Periodo", "Ventas", "Variacion"), show="headings", height=5)
        var_tree.heading("Periodo", text="Periodo")
        var_tree.heading("Ventas", text="Ingresos Ventas")
        var_tree.heading("Variacion", text="Variación %")
        var_tree.column("Periodo", width=85, anchor="center")
        var_tree.column("Ventas", width=115, anchor="e")
        var_tree.column("Variacion", width=95, anchor="center")

        for vp in k.get("variacion_periodos", []):
            pct = vp["variacion_pct"]
            pct_str = "Base" if pct == 0 else f"{pct:+.2f}%"
            var_tree.insert("", tk.END, values=(vp["periodo"], f"${vp['ventas']:,.0f}", pct_str))

        var_tree.pack(fill=tk.BOTH, expand=True)

        # Panel Derecho: Participación Comercial
        pnl_right = tk.Frame(details_frame, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"], padx=12, pady=10)
        pnl_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))

        tk.Label(
            pnl_right,
            text="🥧 Participación Comercial por Región / Segmento",
            font=FONTS["body_bold"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"]
        ).pack(anchor="w", pady=(0, 6))

        part_tree = ttk.Treeview(pnl_right, columns=("Segmento", "Ventas", "Participacion"), show="headings", height=5)
        part_tree.heading("Segmento", text="Región / Segmento")
        part_tree.heading("Ventas", text="Ventas")
        part_tree.heading("Participacion", text="Participación %")
        part_tree.column("Segmento", width=115, anchor="w")
        part_tree.column("Ventas", width=115, anchor="e")
        part_tree.column("Participacion", width=105, anchor="center")

        for row in part_list:
            part_tree.insert("", tk.END, values=(row["segmento"], f"${row['ventas']:,.0f}", f"{row['participacion_pct']:.1f}%"))

        part_tree.pack(fill=tk.BOTH, expand=True)

    def _init_charts_view(self):
        """Construye la vista de gráficos analíticos."""
        charts_frame = ChartsView(
            self.tab_container,
            df=self.df,
            col_map=self.results.get("column_mapping", {})
        )
        self.views["charts"] = charts_frame

    def _init_problems_view(self):
        """Construye la vista de diagnóstico de problemas y plan de acción."""
        problems_frame = ProblemsView(
            self.tab_container,
            problems=self.results.get("problems", [])
        )
        self.views["problems"] = problems_frame

    def _init_data_table_view(self):
        """Construye la vista de tabla con los datos del archivo."""
        table_frame = tk.Frame(self.tab_container, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"])
        self.views["data"] = table_frame
        self.table_builder(table_frame)

    def _export_report(self):
        """Exporta un reporte de diagnóstico en texto / markdown."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Reporte de Texto", "*.txt"), ("Reporte Markdown", "*.md")],
            title="Guardar Informe de Diagnóstico Empresarial"
        )
        if not file_path:
            return

        try:
            k = self.results.get("kpis", {})
            probs = self.results.get("problems", [])
            lines = [
                "============================================================",
                "       INFORME DE DIAGNÓSTICO EMPRESARIAL MULTIDIMENSIONAL",
                "============================================================",
                f"Total de registros evaluados: {self.results.get('total_rows', 0)}",
                "",
                "1. INDICADORES EMPRESARIALES PROCESADOS",
                "------------------------------------------------------------",
                f"• Ingresos por Ventas: ${k.get('ingresos_ventas', 0):,.2f}",
                f"• Unidades Vendidas: {k.get('unidades_vendidas', 0):,}",
                f"• Ticket Promedio (Ingresos / Pedidos): ${k.get('ticket_promedio', 0):,.2f}",
                f"• Margen Bruto: {k.get('margen_bruto_pct', 0):.2f}%",
                f"• Variación de Ventas (último periodo): {k.get('variacion_ventas_ultimo_pct', 0):+.2f}%",
                f"• Crecimiento Global: {k.get('crecimiento_global_pct', 0):+.2f}%",
                "",
                "Participación Comercial por Segmento:",
            ]

            for pt in k.get("participacion_comercial", []):
                lines.append(f"  - {pt['segmento']}: ${pt['ventas']:,.2f} ({pt['participacion_pct']:.1f}%)")

            lines.extend([
                "",
                "2. PROBLEMAS IDENTIFICADOS Y PLAN DE ACCIÓN",
                "------------------------------------------------------------"
            ])

            for p in probs:
                lines.extend([
                    f"[{p.get('nivel')}] {p.get('titulo')} ({p.get('dimension')})",
                    f"  - Hallazgo: {p.get('hallazgo')}",
                    f"  - Causa Raíz Probable: {p.get('causa_probable')}",
                    f"  - Recomendación: {p.get('accion')}",
                    ""
                ])

            lines.append("=================== Fin del Informe ===================")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            messagebox.showinfo("Exportación Exitosa", f"Informe guardado correctamente en:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error al Exportar", f"No se pudo guardar el informe: {str(e)}")
