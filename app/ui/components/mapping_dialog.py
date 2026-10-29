"""
mapping_dialog.py
Diálogo interactivo para mapear columnas de archivos Excel o CSV personalizados.
Garantiza que cualquier archivo Excel, sin importar cómo se llamen sus columnas,
pueda ser analizado correctamente.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional
from app.ui.styles import PALETTE, FONTS


class ColumnMappingDialog(tk.Toplevel):
    """Ventana emergente para asignar columnas a indicadores empresariales."""

    FIELDS = [
        ("ventas", "💰 Ventas / Ingresos (Requerido)", "Columna con el valor monetario o facturación."),
        ("costos", "🏷️ Costos Operativos / COGS", "Costos de productos o gastos para calcular margen."),
        ("margen", "📈 Margen Bruto % (Opcional)", "Si ya viene calculado en porcentaje."),
        ("unidades", "📦 Unidades Vendidas", "Cantidad de piezas o productos vendidos."),
        ("pedidos", "🎫 Pedidos / Transacciones", "Número de órdenes para calcular Ticket Promedio."),
        ("period", "📅 Periodo / Fecha", "Mes, trimestre o fecha para calcular variación temporal."),
        ("region", "🗺️ Región / Sucursal / Zona", "Territorio para calcular participación comercial."),
        ("canal", "🌐 Canal de Venta", "Online, Tienda Física, Mayorista, etc."),
        ("producto", "🛍️ Producto / Categoría", "Nombre o línea de producto para evaluar desempeño."),
        ("precio", "💵 Precio Unitario", "Precio de venta por unidad para sensibilidad de precios."),
        ("stock", "📊 Stock / Inventario", "Existencias para evaluar riesgo de quiebre o sobrestock.")
    ]

    def __init__(self, parent, available_columns: List[str], current_mapping: Dict[str, Optional[str]], on_confirm_callback):
        super().__init__(parent)
        self.title("Asignación de Columnas del Archivo")
        self.geometry("640x680")
        self.minsize(580, 550)
        self.configure(bg=PALETTE["bg_main"])
        self.transient(parent)
        self.grab_set()

        self.available_columns = ["(Ninguna / No disponible)"] + list(available_columns)
        self.current_mapping = current_mapping or {}
        self.on_confirm = on_confirm_callback
        self.combo_vars: Dict[str, tk.StringVar] = {}

        self._build_ui()

    def _build_ui(self):
        # Encabezado
        header = tk.Frame(self, bg=PALETTE["bg_header"], padx=20, pady=16)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="Configuración de Columnas del Archivo",
            font=FONTS["section_title"],
            fg=PALETTE["text_header"],
            bg=PALETTE["bg_header"]
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Confirme o seleccione qué columna de su Excel corresponde a cada indicador empresarial.",
            font=FONTS["caption"],
            fg="#94A3B8",
            bg=PALETTE["bg_header"]
        ).pack(anchor="w", pady=(2, 0))

        # Contenedor con scroll para los campos
        body_container = tk.Frame(self, bg=PALETTE["bg_main"])
        body_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        canvas = tk.Canvas(body_container, bg=PALETTE["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(body_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=PALETTE["bg_main"])

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_win = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_win, width=event.width)

        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Generar selector para cada campo
        for key, label_text, desc in self.FIELDS:
            card = tk.Frame(scrollable_frame, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"], padx=12, pady=8)
            card.pack(fill=tk.X, pady=(0, 6))

            # Fila superior: Nombre del indicador
            row_top = tk.Frame(card, bg=PALETTE["bg_card"])
            row_top.pack(fill=tk.X)

            tk.Label(row_top, text=label_text, font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT)

            # Selector Combobox
            init_val = self.current_mapping.get(key)
            if not init_val or init_val not in self.available_columns:
                init_val = "(Ninguna / No disponible)"

            c_var = tk.StringVar(value=init_val)
            self.combo_vars[key] = c_var

            cb = ttk.Combobox(
                row_top,
                textvariable=c_var,
                values=self.available_columns,
                state="readonly",
                width=28,
                font=("Segoe UI", 9)
            )
            cb.pack(side=tk.RIGHT)

            # Descripción de ayuda
            tk.Label(card, text=desc, font=FONTS["caption"], fg=PALETTE["text_muted"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(2, 0))

        # Barra inferior de acciones
        footer = tk.Frame(self, bg=PALETTE["bg_card"], bd=1, relief="solid", highlightbackground=PALETTE["border"], padx=20, pady=12)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        btn_cancel = tk.Button(
            footer,
            text="Cancelar",
            font=FONTS["body"],
            bg="#F1F5F9",
            fg=PALETTE["text_secondary"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.destroy
        )
        btn_cancel.pack(side=tk.LEFT)

        btn_save = tk.Button(
            footer,
            text="Guardar y Ejecutar Análisis",
            font=FONTS["body_bold"],
            bg=PALETTE["btn_load"],
            fg="#FFFFFF",
            relief="flat",
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._on_save
        )
        btn_save.pack(side=tk.RIGHT)

    def _on_save(self):
        new_map = {}
        for key, var in self.combo_vars.items():
            val = var.get()
            if val == "(Ninguna / No disponible)":
                new_map[key] = None
            else:
                new_map[key] = val

        # Validar si al menos se seleccionó ventas o alguna métrica numérica
        if not new_map.get("ventas"):
            confirm = messagebox.askyesno(
                "Advertencia de Columna",
                "No ha seleccionado ninguna columna para 'Ventas / Ingresos'.\n\n"
                "Sin esta columna, los KPIs financieros y la participación comercial no podrán calcularse.\n"
                "¿Desea continuar de todas formas?"
            )
            if not confirm:
                return

        self.on_confirm(new_map)
        self.destroy()

