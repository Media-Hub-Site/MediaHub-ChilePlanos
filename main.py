"""
ChilePlanos - Aplicación de escritorio nativa de alto rendimiento para arquitectura.
Reescrita con PyQt6 para máxima fluidez, renderizado nativo C++ y respuesta instantánea.
"""
import sys
import os
import math
import json
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, QScrollArea,
    QFrame, QFileDialog, QMessageBox, QDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QCursor

from src_py.database import PLANOS_DATABASE, ESPECIALIDADES, TIPOLOGIAS
from src_py.regiones_chile import REGIONES_CHILE
from src_py.cad_exporter import exportar_plano_dxf, exportar_memoria_tecnica
from src_py.api_client import consultar_poligonos_ciudad

PLANOS_POR_PAGINA = 10

# Pre-procesamiento de índice de búsqueda para filtrado instantáneo O(1)/O(N) sin lag
for p in PLANOS_DATABASE:
    p["_search_corpus"] = f"{p['nombre']} {p['codigo']} {p.get('comuna','')} {p['ubicacion']} {p['especialidad']} {p['tipologia']} {p['descripcion']}".lower()

HOJA_ESTILOS_GLOBAL = """
QMainWindow {
    background-color: #0b1120;
}
QWidget {
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
}
QFrame#Sidebar {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
}
QLabel#TituloApp {
    font-size: 20px;
    font-weight: bold;
    color: #f8fafc;
}
QLabel#SubtituloApp {
    font-size: 11px;
    color: #94a3b8;
}
QLabel#SeccionFiltro {
    font-size: 10px;
    font-weight: bold;
    color: #64748b;
    letter-spacing: 0.5px;
}
QComboBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    color: #f8fafc;
}
QComboBox:hover {
    border: 1px solid #3b82f6;
}
QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #334155;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}
QCheckBox {
    font-size: 12px;
    color: #cbd5e1;
    spacing: 8px;
}
QLineEdit#Buscador {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    color: #f8fafc;
}
QLineEdit#Buscador:focus {
    border: 1px solid #3b82f6;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QFrame#CardPlano {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
}
QFrame#CardPlano:hover {
    border: 1px solid #475569;
}
QLabel#BadgeCodigo {
    background-color: #334155;
    color: #e2e8f0;
    font-size: 10px;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
}
QLabel#BadgeEsp {
    background-color: rgba(30, 64, 175, 0.4);
    color: #93c5fd;
    font-size: 10px;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
}
QLabel#TituloPlano {
    font-size: 14px;
    font-weight: bold;
    color: #f8fafc;
}
QLabel#DescPlano {
    font-size: 11px;
    color: #94a3b8;
    line-height: 1.3;
}
QLabel#MetaPlano {
    font-size: 10px;
    color: #cbd5e1;
}
QPushButton {
    border-radius: 6px;
    font-size: 11px;
    font-weight: bold;
    padding: 6px 12px;
}
QPushButton#BtnDxf {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
}
QPushButton#BtnDxf:hover {
    background-color: #1d4ed8;
}
QPushButton#BtnMemoria {
    background-color: #0f766e;
    color: #ffffff;
    border: none;
}
QPushButton#BtnMemoria:hover {
    background-color: #115e59;
}
QPushButton#BtnFicha {
    background-color: #334155;
    color: #f8fafc;
    border: none;
}
QPushButton#BtnFicha:hover {
    background-color: #475569;
}
QPushButton#BtnFav {
    background-color: #334155;
    color: #cbd5e1;
    border: none;
    font-size: 11px;
    padding: 3px 8px;
}
QPushButton#BtnFavActivo {
    background-color: #b45309;
    color: #ffffff;
    border: none;
    font-size: 11px;
    padding: 3px 8px;
}
QFrame#BarraPaginacion {
    background-color: #1e293b;
    border-radius: 8px;
    padding: 4px;
}
"""

class VentanaDetalles(QDialog):
    def __init__(self, plano, parent=None):
        super().__init__(parent)
        self.plano = plano
        self.setWindowTitle(f"{plano['codigo']} - Ficha Técnica de Arquitectura")
        self.resize(620, 480)
        self.setStyleSheet(HOJA_ESTILOS_GLOBAL)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        lbl_tit = QLabel(plano["nombre"])
        lbl_tit.setObjectName("TituloPlano")
        lbl_tit.setWordWrap(True)
        lbl_tit.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        layout.addWidget(lbl_tit)

        txt_info = (
            f"<b>Especialidad:</b> {plano['especialidad']} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Escala:</b> {plano['escala']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Superficie:</b> {plano['superficie']}<br>"
            f"<b>Ubicación:</b> {plano['ubicacion']}<br>"
            f"<b>Fuente / Normativa:</b> {plano['fuente']}"
        )
        lbl_meta = QLabel(txt_info)
        lbl_meta.setTextFormat(Qt.TextFormat.RichText)
        lbl_meta.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(lbl_meta)

        lbl_sec = QLabel("Criterios Técnicos y Especificaciones de la Lámina:")
        lbl_sec.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        lbl_sec.setStyleSheet("color: #e2e8f0; margin-top: 8px;")
        layout.addWidget(lbl_sec)

        lista_txt = "".join([f"• {e}<br>" for e in plano["especificaciones"]])
        lbl_especs = QLabel(lista_txt)
        lbl_especs.setTextFormat(Qt.TextFormat.RichText)
        lbl_especs.setStyleSheet("color: #cbd5e1; font-size: 11px; margin-left: 8px;")
        lbl_especs.setWordWrap(True)
        layout.addWidget(lbl_especs)

        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_dxf = QPushButton("💾 Guardar Dibujo CAD (.DXF)")
        btn_dxf.setObjectName("BtnDxf")
        btn_dxf.clicked.connect(self.descargar_dxf)

        btn_txt = QPushButton("📄 Guardar Memoria (.TXT)")
        btn_txt.setObjectName("BtnMemoria")
        btn_txt.clicked.connect(self.descargar_txt)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("BtnFicha")
        btn_cerrar.clicked.connect(self.close)

        btn_box.addWidget(btn_dxf)
        btn_box.addWidget(btn_txt)
        btn_box.addWidget(btn_cerrar)
        layout.addLayout(btn_box)

    def descargar_dxf(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, f"Guardar Plano CAD - {self.plano['codigo']}",
            f"{self.plano['codigo']}_{self.plano['especialidad']}_{self.plano.get('comuna','Chile')}.dxf",
            "Dibujo CAD (*.dxf)"
        )
        if ruta:
            try:
                exportar_plano_dxf(self.plano, ruta)
                QMessageBox.information(self, "Descarga Exitosa", f"Plano CAD guardado en:\n{ruta}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo CAD: {e}")

    def descargar_txt(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Memoria Técnica",
            f"Memoria_{self.plano['codigo']}_{self.plano.get('comuna','Chile')}.txt",
            "Documento de Texto (*.txt)"
        )
        if ruta:
            try:
                exportar_memoria_tecnica(self.plano, ruta)
                QMessageBox.information(self, "Guardado", f"Memoria técnica guardada en:\n{ruta}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar la memoria: {e}")


class CardPlanoWidget(QFrame):
    """Widget reutilizable para cada plano, optimizado para renderizado ultra rápido."""
    def __init__(self, parent_app, plano):
        super().__init__()
        self.setObjectName("CardPlano")
        self.parent_app = parent_app
        self.plano = plano

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(5)

        # Header con badges
        header = QHBoxLayout()
        header.setSpacing(6)

        lbl_code = QLabel(f" {plano['codigo']} ")
        lbl_code.setObjectName("BadgeCodigo")
        header.addWidget(lbl_code)

        lbl_esp = QLabel(f" {plano['especialidad']} ")
        lbl_esp.setObjectName("BadgeEsp")
        header.addWidget(lbl_esp)

        header.addStretch()

        es_fav = plano["id"] in parent_app.favoritos
        self.btn_fav = QPushButton("★ Guardado" if es_fav else "☆ Guardar")
        self.btn_fav.setObjectName("BtnFavActivo" if es_fav else "BtnFav")
        self.btn_fav.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_fav.clicked.connect(self.toggle_fav)
        header.addWidget(self.btn_fav)
        layout.addLayout(header)

        # Título
        lbl_title = QLabel(plano["nombre"])
        lbl_title.setObjectName("TituloPlano")
        lbl_title.setWordWrap(True)
        layout.addWidget(lbl_title)

        # Descripción
        lbl_desc = QLabel(plano["descripcion"])
        lbl_desc.setObjectName("DescPlano")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        # Meta
        meta_txt = f"📍 {plano['ubicacion']}   |   📐 Escala: {plano['escala']}   |   🏠 {plano['tipologia']}   |   📁 CAD (.DXF)"
        lbl_meta = QLabel(meta_txt)
        lbl_meta.setObjectName("MetaPlano")
        layout.addWidget(lbl_meta)

        # Barra de botones
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        btn_ficha = QPushButton("👁️ Ficha y Normas")
        btn_ficha.setObjectName("BtnFicha")
        btn_ficha.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_ficha.clicked.connect(lambda: VentanaDetalles(self.plano, self.parent_app).exec())
        btn_bar.addWidget(btn_ficha)

        btn_dxf = QPushButton("💾 Descargar CAD (.DXF)")
        btn_dxf.setObjectName("BtnDxf")
        btn_dxf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_dxf.clicked.connect(self.descargar_dxf)
        btn_bar.addWidget(btn_dxf)

        btn_mem = QPushButton("📄 Memoria (.TXT)")
        btn_mem.setObjectName("BtnMemoria")
        btn_mem.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_mem.clicked.connect(self.descargar_memoria)
        btn_bar.addWidget(btn_mem)

        btn_bar.addStretch()
        layout.addLayout(btn_bar)

    def toggle_fav(self):
        pid = self.plano["id"]
        if pid in self.parent_app.favoritos:
            self.parent_app.favoritos.remove(pid)
        else:
            self.parent_app.favoritos.add(pid)
        self.parent_app.actualizar_filtros_y_pagina()

    def descargar_dxf(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, f"Guardar Plano CAD - {self.plano['codigo']}",
            f"{self.plano['codigo']}_{self.plano['especialidad']}_{self.plano.get('comuna','Chile')}.dxf",
            "Dibujo CAD (*.dxf)"
        )
        if ruta:
            try:
                exportar_plano_dxf(self.plano, ruta)
                QMessageBox.information(self, "Descarga Exitosa", f"Plano CAD generado y guardado en:\n{ruta}\n\nCompatible con AutoCAD y Revit.")
            except Exception as e:
                QMessageBox.critical(self, "Error al guardar", f"No se pudo generar el archivo CAD: {e}")

    def descargar_memoria(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Memoria Técnica",
            f"Memoria_{self.plano['codigo']}_{self.plano.get('comuna','Chile')}.txt",
            "Documento de Texto (*.txt)"
        )
        if ruta:
            try:
                exportar_memoria_tecnica(self.plano, ruta)
                QMessageBox.information(self, "Memoria Guardada", f"Memoria técnica guardada en:\n{ruta}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar la memoria: {e}")


class ChilePlanosApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChilePlanos - Banco Nacional de Planimetría Técnica para Arquitectura")
        self.resize(1240, 800)
        self.setMinimumSize(1000, 640)
        self.setStyleSheet(HOJA_ESTILOS_GLOBAL)

        self.lista_regiones = ["Todas"] + [r["region"] for r in REGIONES_CHILE]
        self.favoritos = set()
        self.pagina_actual = 1
        self.total_paginas = 1
        self.planos_filtrados = []

        # Temporizador para debounce del buscador (evita lag al teclear)
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(120)
        self.debounce_timer.timeout.connect(self._on_busqueda_debounced)

        self._crear_ui()
        self.actualizar_filtros_y_pagina()

    def _crear_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # ------------------- PANEL LATERAL (SIDEBAR) -------------------
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(290)
        layout_side = QVBoxLayout(sidebar)
        layout_side.setContentsMargins(20, 24, 20, 20)
        layout_side.setSpacing(10)

        lbl_logo = QLabel("📐 ChilePlanos")
        lbl_logo.setObjectName("TituloApp")
        layout_side.addWidget(lbl_logo)

        lbl_sub = QLabel("Planimetría Técnica Nacional CAD")
        lbl_sub.setObjectName("SubtituloApp")
        layout_side.addWidget(lbl_sub)
        layout_side.addSpacing(10)

        # Filtro: Solo guardados
        self.chk_favs = QCheckBox("⭐ Ver solo guardados")
        self.chk_favs.stateChanged.connect(self._on_filtro_cambiado)
        layout_side.addWidget(self.chk_favs)
        layout_side.addSpacing(6)

        # Filtro: Región
        lbl_reg = QLabel("REGIÓN DE CHILE")
        lbl_reg.setObjectName("SeccionFiltro")
        layout_side.addWidget(lbl_reg)
        self.cb_region = QComboBox()
        self.cb_region.addItems(self.lista_regiones)
        self.cb_region.currentTextChanged.connect(self._on_filtro_cambiado)
        layout_side.addWidget(self.cb_region)

        # Filtro: Especialidad
        lbl_esp = QLabel("ESPECIALIDAD TÉCNICA")
        lbl_esp.setObjectName("SeccionFiltro")
        layout_side.addWidget(lbl_esp)
        self.cb_esp = QComboBox()
        self.cb_esp.addItems(ESPECIALIDADES)
        self.cb_esp.currentTextChanged.connect(self._on_filtro_cambiado)
        layout_side.addWidget(self.cb_esp)

        # Filtro: Tipología
        lbl_tip = QLabel("TIPOLOGÍA ARQUITECTÓNICA")
        lbl_tip.setObjectName("SeccionFiltro")
        layout_side.addWidget(lbl_tip)
        self.cb_tip = QComboBox()
        self.cb_tip.addItems(TIPOLOGIAS)
        self.cb_tip.currentTextChanged.connect(self._on_filtro_cambiado)
        layout_side.addWidget(self.cb_tip)

        layout_side.addSpacing(12)
        btn_api = QPushButton("🌐 Geodatos Topografía API")
        btn_api.setObjectName("BtnFicha")
        btn_api.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_api.clicked.connect(self.abrir_ventana_api)
        layout_side.addWidget(btn_api)

        layout_side.addStretch()

        lbl_foot = QLabel("16 Regiones de Chile • 650+ Láminas\nCompatible con AutoCAD y Revit (.DXF)\nNormativa OGUC • RIDAA • SEC • NCh433")
        lbl_foot.setStyleSheet("color: #64748b; font-size: 10px; line-height: 1.4;")
        layout_side.addWidget(lbl_foot)

        layout_principal.addWidget(sidebar)

        # ------------------- ÁREA PRINCIPAL -------------------
        main_area = QWidget()
        layout_main = QVBoxLayout(main_area)
        layout_main.setContentsMargins(24, 20, 24, 18)
        layout_main.setSpacing(12)

        # Buscador
        self.input_search = QLineEdit()
        self.input_search.setObjectName("Buscador")
        self.input_search.setPlaceholderText("🔍 Buscar por nombre, comuna (Maipú, Temuco, etc.), código (ARQ-10, TEC-12)...")
        self.input_search.textChanged.connect(lambda: self.debounce_timer.start())
        layout_main.addWidget(self.input_search)

        # Header de contadores
        cont_header = QHBoxLayout()
        self.lbl_contador = QLabel("Cargando catálogo...")
        self.lbl_contador.setStyleSheet("font-size: 13px; font-weight: bold; color: #38bdf8;")
        cont_header.addWidget(self.lbl_contador)

        self.lbl_info_pag = QLabel("")
        self.lbl_info_pag.setStyleSheet("font-size: 11px; color: #94a3b8;")
        cont_header.addStretch()
        cont_header.addWidget(self.lbl_info_pag)
        layout_main.addLayout(cont_header)

        # Scroll Area y Contenedor de Planos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.contenedor_cards = QWidget()
        self.layout_cards = QVBoxLayout(self.contenedor_cards)
        self.layout_cards.setContentsMargins(0, 0, 10, 0)
        self.layout_cards.setSpacing(8)
        self.scroll_area.setWidget(self.contenedor_cards)
        layout_main.addWidget(self.scroll_area)

        # Barra de Paginación Condicional (solo si > 10)
        self.frame_pag = QFrame()
        self.frame_pag.setObjectName("BarraPaginacion")
        self.frame_pag.setFixedHeight(48)
        layout_pag = QHBoxLayout(self.frame_pag)
        layout_pag.setContentsMargins(12, 4, 12, 4)

        self.btn_primera = QPushButton("⏮️ Primera")
        self.btn_primera.setObjectName("BtnFicha")
        self.btn_primera.clicked.connect(self.ir_primera_pagina)
        layout_pag.addWidget(self.btn_primera)

        self.btn_anterior = QPushButton("◀ Anterior")
        self.btn_anterior.setObjectName("BtnFicha")
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        layout_pag.addWidget(self.btn_anterior)

        layout_pag.addStretch()
        self.lbl_ind_pag = QLabel("Página 1 de 1")
        self.lbl_ind_pag.setStyleSheet("font-size: 12px; font-weight: bold; color: #f8fafc;")
        layout_pag.addWidget(self.lbl_ind_pag)
        layout_pag.addStretch()

        self.btn_siguiente = QPushButton("Siguiente ▶")
        self.btn_siguiente.setObjectName("BtnDxf")
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)
        layout_pag.addWidget(self.btn_siguiente)

        self.btn_ultima = QPushButton("Última ⏭️")
        self.btn_ultima.setObjectName("BtnFicha")
        self.btn_ultima.clicked.connect(self.ir_ultima_pagina)
        layout_pag.addWidget(self.btn_ultima)

        layout_main.addWidget(self.frame_pag)
        layout_principal.addWidget(main_area)

    def _on_filtro_cambiado(self):
        self.pagina_actual = 1
        self.actualizar_filtros_y_pagina()

    def _on_busqueda_debounced(self):
        self.pagina_actual = 1
        self.actualizar_filtros_y_pagina()

    def actualizar_filtros_y_pagina(self):
        query = self.input_search.text().strip().lower()
        region_sel = self.cb_region.currentText()
        esp = self.cb_esp.currentText()
        tip = self.cb_tip.currentText()
        solo_favs = self.chk_favs.isChecked()

        # Filtrado optimizado en C-speed
        filtrados = []
        for p in PLANOS_DATABASE:
            if solo_favs and p["id"] not in self.favoritos:
                continue
            if region_sel != "Todas" and p.get("region") != region_sel:
                continue
            if esp != "Todas" and p["especialidad"] != esp:
                continue
            if tip != "Todas" and p["tipologia"] != tip:
                continue
            if query and query not in p["_search_corpus"]:
                continue
            filtrados.append(p)

        self.planos_filtrados = filtrados
        total = len(filtrados)
        self.total_paginas = max(1, math.ceil(total / PLANOS_POR_PAGINA))

        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas

        self.lbl_contador.setText(f"Total: {total} planos disponibles en Chile")
        inicio = (self.pagina_actual - 1) * PLANOS_POR_PAGINA + 1
        fin = min(self.pagina_actual * PLANOS_POR_PAGINA, total)

        # Mostrar u ocultar barra de paginación condicional
        if total > PLANOS_POR_PAGINA:
            self.frame_pag.show()
            self.lbl_info_pag.setText(f"Mostrando {inicio}-{fin} de {total} láminas")
            self.lbl_ind_pag.setText(f"Página {self.pagina_actual} de {self.total_paginas} (10 por página)")
            self.btn_primera.setEnabled(self.pagina_actual > 1)
            self.btn_anterior.setEnabled(self.pagina_actual > 1)
            self.btn_siguiente.setEnabled(self.pagina_actual < self.total_paginas)
            self.btn_ultima.setEnabled(self.pagina_actual < self.total_paginas)
        else:
            self.frame_pag.hide()
            self.lbl_info_pag.setText(f"Mostrando todos los {total} resultados" if total > 0 else "Sin resultados")

        self._renderizar_pagina()

    def _renderizar_pagina(self):
        # Limpieza ultra rápida de widgets
        while self.layout_cards.count():
            item = self.layout_cards.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.planos_filtrados:
            lbl_vacio = QLabel("No se encontraron láminas con los criterios seleccionados.\nPrueba restableciendo los filtros.")
            lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_vacio.setStyleSheet("color: #94a3b8; font-size: 14px; margin-top: 40px;")
            self.layout_cards.addWidget(lbl_vacio)
            return

        inicio_idx = (self.pagina_actual - 1) * PLANOS_POR_PAGINA
        fin_idx = inicio_idx + PLANOS_POR_PAGINA
        planos_pagina = self.planos_filtrados[inicio_idx:fin_idx]

        for plano in planos_pagina:
            card = CardPlanoWidget(self, plano)
            self.layout_cards.addWidget(card)

        self.layout_cards.addStretch()
        self.scroll_area.verticalScrollBar().setValue(0)

    def pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.actualizar_filtros_y_pagina()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_filtros_y_pagina()

    def ir_primera_pagina(self):
        if self.pagina_actual != 1:
            self.pagina_actual = 1
            self.actualizar_filtros_y_pagina()

    def ir_ultima_pagina(self):
        if self.pagina_actual != self.total_paginas:
            self.pagina_actual = self.total_paginas
            self.actualizar_filtros_y_pagina()

    def abrir_ventana_api(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Consulta de Planimetría & Polígonos Urbanos (API)")
        dlg.resize(620, 500)
        dlg.setStyleSheet(HOJA_ESTILOS_GLOBAL)

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel("Extracción de Polígonos de Sitio (Overpass API / OpenStreetMap)")
        lbl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lay.addWidget(lbl)

        inp_city = QLineEdit("Santiago")
        inp_city.setObjectName("Buscador")
        lay.addWidget(inp_city)

        txt_out = QTextEdit()
        txt_out.setStyleSheet("background-color: #020617; color: #38bdf8; font-family: Consolas; font-size: 11px;")
        lay.addWidget(txt_out)

        btn_run = QPushButton("🚀 Ejecutar Consulta API")
        btn_run.setObjectName("BtnDxf")

        def run_api():
            ciudad = inp_city.text().strip() or "Santiago"
            txt_out.setText(f"Consultando geometrías vectoriales para {ciudad}...\n")
            def hilo():
                res = consultar_poligonos_ciudad(ciudad)
                txt = json.dumps(res[:3], indent=2, ensure_ascii=False)
                # Volver al hilo principal
                QTimer.singleShot(0, lambda: txt_out.setText(f"Elementos encontrados: {len(res)}\n\n{txt}"))
            threading.Thread(target=hilo, daemon=True).start()

        btn_run.clicked.connect(run_api)
        lay.addWidget(btn_run)
        dlg.exec()


def main():
    app = QApplication(sys.argv)
    ventana = ChilePlanosApp()
    ventana.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
