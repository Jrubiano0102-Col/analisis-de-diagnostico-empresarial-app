"""
charts_view.py
Componente de gráficos estadísticos y tendencias empresariales embebidos con Matplotlib.
Diseñado con desplazamiento interactivo para que nunca se corte en modo ventana.
"""
import os
import tempfile
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "dairo_matplotlib")

import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from app.ui.styles import PALETTE


class ChartsView(tk.Frame):
    """Panel de gráficos analíticos integrados con scroll para modo ventana."""

    def __init__(self, parent, df: pd.DataFrame, col_map: dict, **kwargs):
        super().__init__(parent, bg=PALETTE["bg_main"], **kwargs)
        self.df = df
        self.col_map = col_map
        self._build_ui()

    def _build_ui(self):
        top_bar = tk.Frame(self, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"], padx=14, pady=8)
        top_bar.pack(fill=tk.X, padx=10, pady=(8, 6))

        lbl = tk.Label(
            top_bar,
            text="📈 Gráficas Analíticas:",
            font=("Segoe UI", 11, "bold"),
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"]
        )
        lbl.pack(side=tk.LEFT)

        self.chart_type_var = tk.StringVar(value="Tablero General de Indicadores (2x2)")
        options = [
            "Tablero General de Indicadores (2x2)",
            "1. Ingresos por Ventas y Variación Temporal",
            "2. Margen Bruto (%) vs Metas por Región",
            "3. Participación Comercial (% de Mercado)",
            "4. Unidades Vendidas y Ticket Promedio",
            "5. Desempeño por Producto y Canal",
            "6. Sensibilidad de Precios e Inventarios"
        ]
        combo = ttk.Combobox(
            top_bar,
            textvariable=self.chart_type_var,
            values=options,
            state="readonly",
            width=42,
            font=("Segoe UI", 9)
        )
        combo.pack(side=tk.LEFT, padx=15)
        combo.bind("<<ComboboxSelected>>", lambda e: self._render_chart())

        # Contenedor con scroll vertical para soportar ventanas pequeñas sin recortar
        outer_container = tk.Frame(self, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"])
        outer_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))

        self.chart_scroll_canvas = tk.Canvas(outer_container, bg="#FFFFFF", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(outer_container, orient="vertical", command=self.chart_scroll_canvas.yview)
        self.canvas_container = tk.Frame(self.chart_scroll_canvas, bg="#FFFFFF")

        self.canvas_container.bind(
            "<Configure>",
            lambda e: self.chart_scroll_canvas.configure(scrollregion=self.chart_scroll_canvas.bbox("all"))
        )
        self.canvas_win = self.chart_scroll_canvas.create_window((0, 0), window=self.canvas_container, anchor="nw")

        def _on_canvas_configure(event):
            self.chart_scroll_canvas.itemconfig(self.canvas_win, width=event.width)

        self.chart_scroll_canvas.bind("<Configure>", _on_canvas_configure)
        self.chart_scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.chart_scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.figure = None
        self.canvas = None
        self.toolbar = None

        self._render_chart()

    def scroll_canvas(self, delta: int):
        """Desplaza el canvas de gráficos verticalmente."""
        try:
            self.chart_scroll_canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        except Exception:
            pass

    def _render_chart(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if self.toolbar:
            self.toolbar.destroy()

        mode = self.chart_type_var.get()
        df = self.df
        cm = self.col_map

        # Tamaño optimizado y adaptable
        fig = Figure(figsize=(8.5, 5.2), dpi=95, facecolor="#FFFFFF")
        
        if "Tablero General" in mode:
            self._render_2x2_dashboard(fig, df, cm)
        elif "1. Ingresos" in mode:
            self._render_single_sales_growth(fig, df, cm)
        elif "2. Margen Bruto" in mode:
            self._render_single_margins(fig, df, cm)
        elif "3. Participación" in mode:
            self._render_single_market_share(fig, df, cm)
        elif "4. Unidades" in mode:
            self._render_single_units_ticket(fig, df, cm)
        elif "5. Desempeño" in mode:
            self._render_product_channel_view(fig, df, cm)
        elif "6. Sensibilidad" in mode:
            self._render_price_inventory_view(fig, df, cm)

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_container)
        self.canvas.draw()
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_container)
        self.toolbar.config(background="#FFFFFF")
        self.toolbar.update()
        
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _render_2x2_dashboard(self, fig: Figure, df: pd.DataFrame, cm: dict):
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, 3)
        ax4 = fig.add_subplot(2, 2, 4)

        period_col = cm["period"] or df.columns[0]
        ventas_col = cm["ventas"]
        costos_col = cm["costos"]
        region_col = cm["region"] or (df.columns[1] if len(df.columns) > 1 else None)
        margen_col = cm["margen"]
        unidades_col = cm["unidades"]
        pedidos_col = cm["pedidos"]

        if ventas_col and period_col:
            grp = df.groupby(period_col)[[ventas_col] + ([costos_col] if costos_col else [])].sum()
            x = np.arange(len(grp))
            w = 0.35
            ax1.bar(x - w/2, grp[ventas_col] / 1000, w, label="Ventas ($K)", color="#2563EB")
            if costos_col:
                ax1.bar(x + w/2, grp[costos_col] / 1000, w, label="Costos ($K)", color="#94A3B8")
            ax1.set_title("1. Ingresos por Ventas vs Costos", fontsize=9, fontweight="bold", pad=4)
            ax1.set_xticks(x)
            ax1.set_xticklabels(grp.index, rotation=18, fontsize=8)
            ax1.legend(fontsize=7)
            ax1.grid(axis="y", linestyle="--", alpha=0.3)
        else:
            self._empty_chart_msg(ax1, "Ingresos no disponibles")

        if region_col and margen_col and pd.api.types.is_numeric_dtype(df[margen_col]):
            margen_reg = df.groupby(region_col)[margen_col].mean().sort_values()
            colors = ["#EF4444" if v < 20 else ("#F59E0B" if v < 35 else "#10B981") for v in margen_reg.values]
            ax2.barh(margen_reg.index.astype(str), margen_reg.values, color=colors, height=0.5)
            ax2.axvline(30, color="#1E3A8A", linestyle=":", linewidth=1.2, label="Meta 30%")
            ax2.set_title("2. Margen Bruto (%) por Región", fontsize=9, fontweight="bold", pad=4)
            ax2.legend(fontsize=7)
            ax2.grid(axis="x", linestyle="--", alpha=0.3)
        else:
            self._empty_chart_msg(ax2, "Margen Bruto no disponible")

        if region_col and ventas_col and pd.api.types.is_numeric_dtype(df[ventas_col]):
            part_series = df.groupby(region_col)[ventas_col].sum()
            colors_pie = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899"]
            wedges, texts, autotexts = ax3.pie(
                part_series.values,
                labels=part_series.index.astype(str),
                autopct="%1.1f%%",
                startangle=140,
                colors=colors_pie[:len(part_series)],
                textprops=dict(fontsize=8)
            )
            for at in autotexts:
                at.set_fontsize(7)
                at.set_color("#FFFFFF")
            ax3.set_title("3. Participación Comercial (%)", fontsize=9, fontweight="bold", pad=4)
        else:
            self._empty_chart_msg(ax3, "Participación no disponible")

        if unidades_col and period_col and pd.api.types.is_numeric_dtype(df[unidades_col]):
            unidades_grp = df.groupby(period_col)[unidades_col].sum()
            ax4.plot(unidades_grp.index.astype(str), unidades_grp.values, marker="o", color="#0D9488", linewidth=2)
            ax4.set_title("4. Unidades Vendidas por Periodo", fontsize=9, fontweight="bold", pad=4)
            ax4.set_xticks(range(len(unidades_grp)))
            ax4.set_xticklabels(unidades_grp.index.astype(str), rotation=18, fontsize=8)
            ax4.grid(True, linestyle="--", alpha=0.3)
        elif pedidos_col and period_col and pd.api.types.is_numeric_dtype(df[pedidos_col]):
            pedidos_grp = df.groupby(period_col)[pedidos_col].sum()
            ax4.bar(pedidos_grp.index.astype(str), pedidos_grp.values, color="#7C3AED", width=0.45)
            ax4.set_title("4. Número de Pedidos por Periodo", fontsize=9, fontweight="bold", pad=4)
            ax4.grid(axis="y", linestyle="--", alpha=0.3)
        else:
            self._empty_chart_msg(ax4, "Unidades/Pedidos no disponibles")

    def _render_single_sales_growth(self, fig: Figure, df: pd.DataFrame, cm: dict):
        ax = fig.add_subplot(1, 1, 1)
        period_col = cm["period"] or df.columns[0]
        ventas_col = cm["ventas"]
        if ventas_col and period_col:
            grp = df.groupby(period_col, sort=False)[ventas_col].sum()
            periods = list(grp.index.astype(str))
            values = list(grp.values)
            
            bars = ax.bar(periods, [v / 1000 for v in values], color="#3B82F6", width=0.5, label="Ventas ($K USD)")
            for i, bar in enumerate(bars):
                h = bar.get_height()
                if i > 0 and values[i-1] > 0:
                    var = ((values[i] - values[i-1]) / values[i-1]) * 100
                    var_str = f"{var:+.1f}%"
                    color_var = "#10B981" if var >= 0 else "#EF4444"
                else:
                    var_str = "Base"
                    color_var = "#64748B"
                
                ax.text(bar.get_x() + bar.get_width()/2., h + 2, f"${h:,.0f}K\n({var_str})",
                        ha="center", va="bottom", fontsize=8, fontweight="bold", color=color_var)

            ax.set_title("Ingresos por Ventas y Variación Porcentual entre Periodos", fontsize=11, fontweight="bold")
            ax.set_ylabel("Ingresos ($ Miles USD)", fontsize=9)
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            ax.legend(fontsize=8)
        else:
            self._empty_chart_msg(ax, "Datos de ingresos insuficientes")

    def _render_single_margins(self, fig: Figure, df: pd.DataFrame, cm: dict):
        ax = fig.add_subplot(1, 1, 1)
        region_col = cm["region"] or df.columns[1]
        margen_col = cm["margen"]
        if region_col and margen_col and pd.api.types.is_numeric_dtype(df[margen_col]):
            margen_reg = df.groupby(region_col)[margen_col].mean().sort_values()
            colors = ["#EF4444" if v < 20 else ("#F59E0B" if v < 35 else "#10B981") for v in margen_reg.values]
            bars = ax.barh(margen_reg.index.astype(str), margen_reg.values, color=colors, height=0.5)
            for bar in bars:
                w = bar.get_width()
                ax.text(w + 0.8, bar.get_y() + bar.get_height()/2., f"{w:.1f}%",
                        va="center", ha="left", fontsize=9, fontweight="bold", color="#1E293B")
            ax.axvline(30, color="#1E3A8A", linestyle="--", linewidth=1.5, label="Meta Deseada (30%)")
            ax.set_title("Margen Bruto (%) por Región / Unidad Comercial", fontsize=11, fontweight="bold")
            ax.set_xlabel("Margen Bruto (%)", fontsize=9)
            ax.legend(fontsize=8)
            ax.grid(axis="x", linestyle="--", alpha=0.3)
        else:
            self._empty_chart_msg(ax, "Datos de margen insuficientes")

    def _render_single_market_share(self, fig: Figure, df: pd.DataFrame, cm: dict):
        ax = fig.add_subplot(1, 1, 1)
        region_col = cm["region"] or cm["dimension"]
        ventas_col = cm["ventas"]
        if region_col and ventas_col and pd.api.types.is_numeric_dtype(df[ventas_col]):
            part = df.groupby(region_col)[ventas_col].sum()
            colors = ["#2563EB", "#0D9488", "#F59E0B", "#8B5CF6", "#EC4899", "#64748B"]
            wedges, texts, autotexts = ax.pie(
                part.values,
                labels=[f"{idx}\n(${val:,.0f})" for idx, val in part.items()],
                autopct="%1.1f%%",
                startangle=140,
                colors=colors[:len(part)],
                textprops=dict(fontsize=8),
                explode=[0.05 if i == 0 else 0 for i in range(len(part))]
            )
            for at in autotexts:
                at.set_fontsize(8)
                at.set_fontweight("bold")
                at.set_color("#FFFFFF")
            ax.set_title("Participación Comercial (% del Total de Ventas)", fontsize=11, fontweight="bold")
        else:
            self._empty_chart_msg(ax, "Datos de participación insuficientes")

    def _render_single_units_ticket(self, fig: Figure, df: pd.DataFrame, cm: dict):
        ax1 = fig.add_subplot(1, 1, 1)
        period_col = cm["period"] or df.columns[0]
        unidades_col = cm["unidades"]
        ventas_col = cm["ventas"]
        pedidos_col = cm["pedidos"]

        if period_col and (unidades_col or pedidos_col):
            ax2 = ax1.twinx()
            if unidades_col and pd.api.types.is_numeric_dtype(df[unidades_col]):
                u_grp = df.groupby(period_col)[unidades_col].sum()
                ax1.plot(u_grp.index.astype(str), u_grp.values, color="#0D9488", marker="o", linewidth=2.5, label="Unidades Vendidas")
                ax1.set_ylabel("Unidades Vendidas", color="#0D9488", fontsize=9)

            if pedidos_col and ventas_col and pd.api.types.is_numeric_dtype(df[pedidos_col]) and pd.api.types.is_numeric_dtype(df[ventas_col]):
                p_grp = df.groupby(period_col)[pedidos_col].sum()
                v_grp = df.groupby(period_col)[ventas_col].sum()
                ticket_series = v_grp / p_grp
                ax2.plot(ticket_series.index.astype(str), ticket_series.values, color="#7C3AED", marker="s", linestyle="--", linewidth=2, label="Ticket Promedio ($)")
                ax2.set_ylabel("Ticket Promedio ($ USD)", color="#7C3AED", fontsize=9)

            ax1.set_title("Evolución de Unidades Vendidas y Ticket Promedio por Periodo", fontsize=11, fontweight="bold")
            ax1.grid(True, linestyle="--", alpha=0.3)
        else:
            self._empty_chart_msg(ax1, "Columnas de unidades o pedidos no encontradas")

    def _render_product_channel_view(self, fig: Figure, df: pd.DataFrame, cm: dict):
        ax1 = fig.add_subplot(1, 2, 1)
        ax2 = fig.add_subplot(1, 2, 2)

        prod_col = cm["producto"]
        canal_col = cm["canal"]
        ventas_col = cm["ventas"]

        if prod_col and ventas_col:
            prod_s = df.groupby(prod_col)[ventas_col].sum().sort_values(ascending=True)
            ax1.barh(prod_s.index.astype(str), prod_s.values / 1000, color="#3B82F6", height=0.5)
            ax1.set_title("Ventas por Producto ($K USD)", fontsize=9, fontweight="bold")
            ax1.set_xlabel("Ventas ($K USD)", fontsize=8)
            ax1.grid(axis="x", linestyle="--", alpha=0.3)
        else:
            self._empty_chart_msg(ax1, "Columna de producto no encontrada")

        if canal_col and ventas_col:
            canal_s = df.groupby(canal_col)[ventas_col].sum().sort_values(ascending=True)
            ax2.barh(canal_s.index.astype(str), canal_s.values / 1000, color="#10B981", height=0.5)
            ax2.set_title("Ventas por Canal ($K USD)", fontsize=9, fontweight="bold")
            ax2.set_xlabel("Ventas ($K USD)", fontsize=8)
            ax2.grid(axis="x", linestyle="--", alpha=0.3)
        else:
            self._empty_chart_msg(ax2, "Columna de canal no encontrada")

    def _render_price_inventory_view(self, fig: Figure, df: pd.DataFrame, cm: dict):
        ax1 = fig.add_subplot(1, 2, 1)
        ax2 = fig.add_subplot(1, 2, 2)

        prod_col = cm["producto"]
        stock_col = cm["stock"]
        precio_col = cm["precio"]
        unidades_col = cm["unidades"]
        ventas_col = cm["ventas"]

        if prod_col and stock_col and pd.api.types.is_numeric_dtype(df[stock_col]):
            stock_min = df.groupby(prod_col)[stock_col].min()
            stock_max = df.groupby(prod_col)[stock_col].max()
            x = np.arange(len(stock_min))
            w = 0.35
            ax1.bar(x - w/2, stock_min.values, w, label="Stock Mínimo", color="#EF4444")
            ax1.bar(x + w/2, stock_max.values, w, label="Stock Máximo", color="#3B82F6")
            ax1.set_title("Inventario: Stock Mín vs Máx", fontsize=9, fontweight="bold")
            ax1.set_xticks(x)
            ax1.set_xticklabels(stock_min.index.astype(str), rotation=18, fontsize=8)
            ax1.legend(fontsize=7)
            ax1.grid(axis="y", linestyle="--", alpha=0.3)
        else:
            self._empty_chart_msg(ax1, "Datos de stock/inventario no disponibles")

        if (precio_col or (ventas_col and unidades_col)) and unidades_col:
            p_vals = df[precio_col] if precio_col else (df[ventas_col] / df[unidades_col])
            u_vals = df[unidades_col]
            ax2.scatter(p_vals, u_vals, color="#7C3AED", alpha=0.7, edgecolors="none", s=40)
            ax2.set_title("Sensibilidad: Precio vs Unidades", fontsize=9, fontweight="bold")
            ax2.set_xlabel("Precio Unitario ($)", fontsize=8)
            ax2.set_ylabel("Unidades Vendidas", fontsize=8)
            ax2.grid(True, linestyle="--", alpha=0.3)
        else:
            self._empty_chart_msg(ax2, "Datos de precio/unidades no disponibles")

    def _empty_chart_msg(self, ax, msg: str):
        ax.text(0.5, 0.5, msg, horizontalalignment="center", verticalalignment="center",
                transform=ax.transAxes, color="#94A3B8", fontsize=9, style="italic")
        ax.set_xticks([])
        ax.set_yticks([])
