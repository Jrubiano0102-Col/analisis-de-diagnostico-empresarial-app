"""
kpi_card.py
Tarjeta visual para presentación de indicadores clave (KPIs).
"""
import tkinter as tk
from app.ui.styles import PALETTE, FONTS


class KPICard(tk.Frame):
    """Tarjeta moderna para visualización de un KPI empresarial."""

    def __init__(self, parent, dimension: str, title: str, value: str,
                 subtitle: str, status: str = "ÓPTIMO", status_color: str = "#10B981", **kwargs):
        super().__init__(parent, bg=PALETTE["bg_card"], bd=1, relief="solid",
                         highlightbackground=PALETTE["border"], padx=16, pady=14, **kwargs)

        self.dimension = dimension
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.status = status
        self.status_color = status_color

        self._build_card()

    def _build_card(self):
        # Cabecera de la tarjeta: Dimensión + Badge de Estado
        header = tk.Frame(self, bg=PALETTE["bg_card"])
        header.pack(fill=tk.X)

        lbl_dim = tk.Label(
            header,
            text=self.dimension.upper(),
            font=("Segoe UI", 8, "bold"),
            fg=PALETTE["text_muted"],
            bg=PALETTE["bg_card"]
        )
        lbl_dim.pack(side=tk.LEFT)

        lbl_badge = tk.Label(
            header,
            text=f"● {self.status}",
            font=("Segoe UI", 8, "bold"),
            fg=self.status_color,
            bg="#F8FAFC",
            padx=6,
            pady=2
        )
        lbl_badge.pack(side=tk.RIGHT)

        # Título del KPI
        lbl_title = tk.Label(
            self,
            text=self.title,
            font=FONTS["body_bold"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_card"],
            anchor="w"
        )
        lbl_title.pack(anchor="w", pady=(6, 2))

        # Valor Principal (Grande)
        lbl_val = tk.Label(
            self,
            text=self.value,
            font=("Segoe UI", 18, "bold"),
            fg=PALETTE["btn_load"],
            bg=PALETTE["bg_card"],
            anchor="w"
        )
        lbl_val.pack(anchor="w")

        # Subtítulo explicativo / contexto
        lbl_sub = tk.Label(
            self,
            text=self.subtitle,
            font=FONTS["caption"],
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_card"],
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(4, 0))

