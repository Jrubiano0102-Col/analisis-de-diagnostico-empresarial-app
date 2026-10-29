"""
problems_view.py
Componente de visualización del diagnóstico causal de problemas y situaciones que requieren atención.
Organizado por las 6 situaciones críticas, con scroll interactivo y rueda del ratón fluida.
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any
from app.ui.styles import PALETTE, FONTS


class ProblemsView(tk.Frame):
    """Panel visual para diagnóstico de problemas detectados."""

    def __init__(self, parent, problems: List[Dict[str, Any]], **kwargs):
        super().__init__(parent, bg=PALETTE["bg_main"], **kwargs)
        self.all_problems = problems or []
        self.current_filter = "all"
        self._build_ui()

    def _build_ui(self):
        # 1. Resumen de Alertas en la parte superior
        summary_bar = tk.Frame(self, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"], padx=16, pady=10)
        summary_bar.pack(fill=tk.X, padx=10, pady=(10, 8))

        crit_count = sum(1 for p in self.all_problems if p.get("nivel") == "CRÍTICO")
        alert_count = sum(1 for p in self.all_problems if p.get("nivel") == "ALERTA")
        ok_count = sum(1 for p in self.all_problems if p.get("nivel") == "ÓPTIMO")

        title_lbl = tk.Label(
            summary_bar,
            text="🚨 Situaciones de Atención y Diagnóstico Causal",
            font=FONTS["section_title"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"]
        )
        title_lbl.pack(side=tk.LEFT)

        badges_frame = tk.Frame(summary_bar, bg=PALETTE["bg_card"])
        badges_frame.pack(side=tk.RIGHT)

        if crit_count > 0:
            tk.Label(
                badges_frame,
                text=f"● {crit_count} Críticos",
                font=("Segoe UI", 9, "bold"),
                fg="#DC2626",
                bg="#FEE2E2",
                padx=8,
                pady=2
            ).pack(side=tk.LEFT, padx=4)

        if alert_count > 0:
            tk.Label(
                badges_frame,
                text=f"● {alert_count} Alertas",
                font=("Segoe UI", 9, "bold"),
                fg="#D97706",
                bg="#FEF3C7",
                padx=8,
                pady=2
            ).pack(side=tk.LEFT, padx=4)

        if ok_count > 0:
            tk.Label(
                badges_frame,
                text=f"● {ok_count} Saludables",
                font=("Segoe UI", 9, "bold"),
                fg="#059669",
                bg="#D1FAE5",
                padx=8,
                pady=2
            ).pack(side=tk.LEFT, padx=4)

        # 2. Barra de Filtros por Situación
        filter_bar = tk.Frame(self, bg=PALETTE["bg_main"])
        filter_bar.pack(fill=tk.X, padx=10, pady=(0, 8))

        filters = [
            ("all", f"Todos ({len(self.all_problems)})"),
            ("periodo", "📉 Ventas en Periodos"),
            ("producto", "📦 Productos"),
            ("region", "🗺️ Regiones"),
            ("canal", "🌐 Canales"),
            ("precio", "🏷️ Precios"),
            ("inventario", "📊 Inventarios"),
        ]

        self.filter_buttons = {}
        for fid, text in filters:
            btn = tk.Button(
                filter_bar,
                text=text,
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                bd=0,
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda f=fid: self._apply_filter(f)
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
            self.filter_buttons[fid] = btn

        # 3. Contenedor con scroll para tarjetas de problemas
        container = tk.Frame(self, bg=PALETTE["bg_main"])
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(container, bg=PALETTE["bg_main"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=PALETTE["bg_main"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", _on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enlace de mousewheel en canvas y contenedor
        self.canvas.bind("<MouseWheel>", lambda e: self.scroll_canvas(e.delta))
        self.scrollable_frame.bind("<MouseWheel>", lambda e: self.scroll_canvas(e.delta))

        self._apply_filter("all")

    def scroll_canvas(self, delta: int):
        """Desplaza el canvas verticalmente de forma suave con la rueda del ratón."""
        try:
            self.canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        except Exception:
            pass

    def _bind_mousewheel_recursive(self, widget):
        """Enlaza el evento de rueda del ratón al widget y a todos sus hijos."""
        try:
            widget.bind("<MouseWheel>", lambda e: self.scroll_canvas(e.delta), add="+")
        except Exception:
            pass
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)

    def _apply_filter(self, fid: str):
        self.current_filter = fid

        # Actualizar estilo de botones
        for key, btn in self.filter_buttons.items():
            if key == fid:
                btn.config(bg=PALETTE["btn_load"], fg="#FFFFFF")
            else:
                btn.config(bg="#E2E8F0", fg=PALETTE["text_primary"])

        # Limpiar contenedor de tarjetas
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        # Filtrar problemas
        if fid == "all":
            matched = self.all_problems
        else:
            matched = [
                p for p in self.all_problems
                if fid in p.get("tipo", "").lower() or fid in p.get("dimension", "").lower() or fid in p.get("id", "").lower()
            ]

        if not matched:
            no_prob = tk.Frame(self.scrollable_frame, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"], padx=20, pady=20)
            no_prob.pack(fill=tk.X, pady=10)
            tk.Label(no_prob, text="✅ No se detectaron situaciones críticas para este criterio.", font=FONTS["body_bold"], fg="#059669", bg=PALETTE["bg_card"]).pack()
            self._bind_mousewheel_recursive(self.scrollable_frame)
            return

        for prob in matched:
            self._render_problem_card(self.scrollable_frame, prob)

        # Enlazar rueda del ratón a cada una de las nuevas tarjetas y etiquetas creadas
        self._bind_mousewheel_recursive(self.scrollable_frame)

    def _render_problem_card(self, parent, prob: Dict[str, Any]):
        nivel = prob.get("nivel", "INFO")
        colors = {
            "CRÍTICO": {"bg_border": "#FCA5A5", "badge_fg": "#991B1B", "badge_bg": "#FEE2E2", "icon": "🔴"},
            "ALERTA": {"bg_border": "#FCD34D", "badge_fg": "#92400E", "badge_bg": "#FEF3C7", "icon": "🟡"},
            "ÓPTIMO": {"bg_border": "#86EFAC", "badge_fg": "#166534", "badge_bg": "#DCFCE7", "icon": "🟢"}
        }.get(nivel, {"bg_border": "#E2E8F0", "badge_fg": "#1E293B", "badge_bg": "#F1F5F9", "icon": "ℹ️"})

        card = tk.Frame(
            parent,
            bg=PALETTE["bg_card"],
            bd=1,
            relief="solid",
            highlightbackground=colors["bg_border"],
            padx=16,
            pady=12
        )
        card.pack(fill=tk.X, pady=(0, 10))

        # Encabezado
        top = tk.Frame(card, bg=PALETTE["bg_card"])
        top.pack(fill=tk.X)

        tipo_str = f" • {prob.get('tipo')}" if prob.get("tipo") else ""
        tk.Label(
            top,
            text=f"{colors['icon']} [{prob.get('dimension', 'General')}{tipo_str}] {prob.get('titulo', 'Situación')}",
            font=FONTS["body_bold"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"]
        ).pack(side=tk.LEFT)

        tk.Label(
            top,
            text=nivel,
            font=("Segoe UI", 8, "bold"),
            fg=colors["badge_fg"],
            bg=colors["badge_bg"],
            padx=8,
            pady=2
        ).pack(side=tk.RIGHT)

        # Hallazgo
        tk.Label(
            card,
            text="📊 Hallazgo Cuantitativo:",
            font=("Segoe UI", 9, "bold"),
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_card"]
        ).pack(anchor="w", pady=(6, 2))

        tk.Label(
            card,
            text=prob.get("hallazgo", ""),
            font=FONTS["body"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"],
            wraplength=880,
            justify="left"
        ).pack(anchor="w", padx=8)

        # Causa Raíz
        tk.Label(
            card,
            text="🔍 Causa Raíz Probable:",
            font=("Segoe UI", 9, "bold"),
            fg="#B45309",
            bg=PALETTE["bg_card"]
        ).pack(anchor="w", pady=(6, 2))

        tk.Label(
            card,
            text=prob.get("causa_probable", ""),
            font=FONTS["body"],
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_card"],
            wraplength=880,
            justify="left"
        ).pack(anchor="w", padx=8)

        # Plan de Acción
        tk.Label(
            card,
            text="💡 Plan de Acción Recomendado:",
            font=("Segoe UI", 9, "bold"),
            fg="#047857",
            bg=PALETTE["bg_card"]
        ).pack(anchor="w", pady=(6, 2))

        tk.Label(
            card,
            text=prob.get("accion", ""),
            font=FONTS["body_bold"],
            fg="#065F46",
            bg="#ECFDF5",
            padx=8,
            pady=5,
            wraplength=880,
            justify="left"
        ).pack(anchor="w", padx=8, fill=tk.X, pady=(2, 0))
