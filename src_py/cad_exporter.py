"""
Generador y exportador de archivos CAD (.DXF) y memorias técnicas reales.
Crea archivos de dibujo CAD compatibles directamente con AutoCAD, Revit, LibreCAD, ArchiCAD.
"""
import ezdxf
from ezdxf import colors
import json
import os

def configurar_capas_estandar(doc):
    """Crea capas estándar de arquitectura (AIA CAD Layer Guidelines)."""
    capas = [
        ("A-MURO", colors.WHITE, "Muros perimetrales e interiores"),
        ("A-EJE", colors.RED, "Ejes estructurales y líneas de centro"),
        ("A-COTA", colors.GREEN, "Cotas y dimensionamiento"),
        ("A-TEXT", colors.YELLOW, "Textos, nombres de recintos y notas"),
        ("A-VANO", colors.CYAN, "Puertas y ventanas"),
        ("MEP-SANI", colors.MAGENTA, "Red de alcantarillado y cámaras"),
        ("MEP-ELEC", colors.BLUE, "Alumbrado, enchufes y tableros"),
        ("S-ESTR", colors.YELLOW, "Fundaciones, vigas y enfierraduras"),
        ("C-TECHO", colors.CYAN, "Cerchas, limatesas y cubierta")
    ]
    for nombre, color, desc in capas:
        if nombre not in doc.layers:
            layer = doc.layers.add(nombre)
            layer.color = color
            layer.description = desc

def exportar_plano_dxf(plano: dict, ruta_destino: str):
    """
    Genera un archivo DXF real con entidades vectoriales CAD según la especialidad del plano.
    """
    doc = ezdxf.new("R2010", setup=True)
    configurar_capas_estandar(doc)
    msp = doc.modelspace()

    esp = plano.get("especialidad", "Arquitectura")

    # Cuadro de rotulación / Viñeta técnica profesional
    _dibujar_vineta(msp, plano)

    if esp == "Arquitectura":
        _dibujar_planta_arquitectura(msp, plano)
    elif esp == "Techumbre":
        _dibujar_cercha_techumbre(msp, plano)
    elif esp == "Alcantarillado":
        _dibujar_red_alcantarillado(msp, plano)
    elif esp == "Eléctrico":
        _dibujar_red_electrica(msp, plano)
    elif esp == "Estructural":
        _dibujar_fundaciones_estructura(msp, plano)
    elif esp == "Detalles":
        _dibujar_corte_escantillon(msp, plano)
    elif esp == "Planimetría General":
        _dibujar_topografia_emplazamiento(msp, plano)
    else:
        _dibujar_geometria_generica(msp, plano)

    doc.saveas(ruta_destino)
    return ruta_destino

def _dibujar_vineta(msp, plano):
    """Dibuja el marco general y cuadro de rotulación (viñeta) del proyecto."""
    # Marco exterior lámina (A1 aprox en metros escala 1:1 modelo)
    msp.add_lwpolyline([(0, 0), (28, 0), (28, 20), (0, 20), (0, 0)], dxfattribs={"layer": "A-MURO"})
    msp.add_lwpolyline([(0.5, 0.5), (27.5, 0.5), (27.5, 19.5), (0.5, 19.5), (0.5, 0.5)], dxfattribs={"layer": "A-EJE"})

    # Cuadro de rotulación (esquina inferior derecha)
    vx, vy = 19.0, 0.5
    msp.add_lwpolyline([(vx, vy), (27.5, vy), (27.5, vy + 4.5), (vx, vy + 4.5), (vx, vy)], dxfattribs={"layer": "A-MURO"})
    
    msp.add_text("PROYECTO: " + plano.get("nombre", "PLANO TÉCNICO"), dxfattribs={"layer": "A-TEXT", "height": 0.22}).set_placement((vx + 0.3, vy + 3.8))
    msp.add_text("ESPECIALIDAD: " + plano.get("especialidad", "").upper(), dxfattribs={"layer": "A-TEXT", "height": 0.20}).set_placement((vx + 0.3, vy + 3.3))
    msp.add_text("CÓDIGO: " + plano.get("codigo", ""), dxfattribs={"layer": "A-TEXT", "height": 0.28}).set_placement((vx + 0.3, vy + 2.6))
    msp.add_text("UBICACIÓN: " + plano.get("ubicacion", ""), dxfattribs={"layer": "A-TEXT", "height": 0.18}).set_placement((vx + 0.3, vy + 2.0))
    msp.add_text("ESCALA: " + plano.get("escala", "1:50") + "  |  SUPERFICIE: " + plano.get("superficie", "N/A"), dxfattribs={"layer": "A-TEXT", "height": 0.18}).set_placement((vx + 0.3, vy + 1.5))
    msp.add_text("FUENTE: " + plano.get("fuente", "CHILEPLANOS"), dxfattribs={"layer": "A-TEXT", "height": 0.15}).set_placement((vx + 0.3, vy + 1.0))
    msp.add_text("SISTEMA DE REFERENCIA: E.P.S. CHILE / OGUC", dxfattribs={"layer": "A-TEXT", "height": 0.13}).set_placement((vx + 0.3, vy + 0.5))

def _dibujar_planta_arquitectura(msp, plano):
    """Genera geometría CAD de planta de arquitectura con recintos, vanos y ejes."""
    # Ejes
    msp.add_line((2, 16), (17, 16), dxfattribs={"layer": "A-EJE", "linetype": "CENTER"})
    msp.add_line((2, 10), (17, 10), dxfattribs={"layer": "A-EJE", "linetype": "CENTER"})
    msp.add_line((2, 4), (17, 4), dxfattribs={"layer": "A-EJE", "linetype": "CENTER"})
    msp.add_line((4, 2), (4, 18), dxfattribs={"layer": "A-EJE", "linetype": "CENTER"})
    msp.add_line((10, 2), (10, 18), dxfattribs={"layer": "A-EJE", "linetype": "CENTER"})
    msp.add_line((15, 2), (15, 18), dxfattribs={"layer": "A-EJE", "linetype": "CENTER"})

    # Muros exteriores (Doble línea)
    msp.add_lwpolyline([(4, 4), (15, 4), (15, 16), (4, 16), (4, 4)], dxfattribs={"layer": "A-MURO"})
    msp.add_lwpolyline([(4.2, 4.2), (14.8, 4.2), (14.8, 15.8), (4.2, 15.8), (4.2, 4.2)], dxfattribs={"layer": "A-MURO"})

    # Muros divisorios interiores
    msp.add_line((10, 4.2), (10, 15.8), dxfattribs={"layer": "A-MURO"})
    msp.add_line((10.15, 4.2), (10.15, 15.8), dxfattribs={"layer": "A-MURO"})
    msp.add_line((4.2, 10), (14.8, 10), dxfattribs={"layer": "A-MURO"})
    msp.add_line((4.2, 10.15), (14.8, 10.15), dxfattribs={"layer": "A-MURO"})

    # Textos de Recintos
    msp.add_text("ESTAR / COMEDOR\nN.P.T. +0.30", dxfattribs={"layer": "A-TEXT", "height": 0.28}).set_placement((5.5, 6.8))
    msp.add_text("COCINA / SERVICIOS\nN.P.T. +0.30", dxfattribs={"layer": "A-TEXT", "height": 0.28}).set_placement((11.2, 6.8))
    msp.add_text("DORMITORIO 1\nN.P.T. +0.30", dxfattribs={"layer": "A-TEXT", "height": 0.28}).set_placement((5.5, 12.8))
    msp.add_text("DORMITORIO 2 / ESTUDIO\nN.P.T. +0.30", dxfattribs={"layer": "A-TEXT", "height": 0.28}).set_placement((11.2, 12.8))

    # Cotas
    msp.add_text("6.00 m", dxfattribs={"layer": "A-COTA", "height": 0.22}).set_placement((6.8, 3.2))
    msp.add_text("5.00 m", dxfattribs={"layer": "A-COTA", "height": 0.22}).set_placement((12.2, 3.2))

def _dibujar_cercha_techumbre(msp, plano):
    """Genera perfil de cercha tipo Howe/Pratt de madera aserrada con pendolón y diagonales."""
    # Cuerda inferior (Tirante)
    msp.add_line((3, 6), (17, 6), dxfattribs={"layer": "C-TECHO"})
    msp.add_line((3, 6.2), (17, 6.2), dxfattribs={"layer": "C-TECHO"})

    # Cuerdas superiores (Pares)
    cumbrera = (10, 11)
    msp.add_line((3, 6), cumbrera, dxfattribs={"layer": "C-TECHO"})
    msp.add_line((17, 6), cumbrera, dxfattribs={"layer": "C-TECHO"})

    # Pendolón central
    msp.add_line((10, 6), cumbrera, dxfattribs={"layer": "C-TECHO"})

    # Diagonales y montantes
    msp.add_line((6.5, 6), (6.5, 8.5), dxfattribs={"layer": "C-TECHO"})
    msp.add_line((6.5, 6), (10, 11), dxfattribs={"layer": "C-TECHO"})
    msp.add_line((13.5, 6), (13.5, 8.5), dxfattribs={"layer": "C-TECHO"})
    msp.add_line((13.5, 6), (10, 11), dxfattribs={"layer": "C-TECHO"})

    # Anotaciones
    msp.add_text("CERCHA TIPO T-1 (PINO RADIATA 2x5\")", dxfattribs={"layer": "A-TEXT", "height": 0.35}).set_placement((5.0, 12.5))
    msp.add_text("PENDIENTE CUBIERTA = 35%", dxfattribs={"layer": "A-TEXT", "height": 0.25}).set_placement((11.0, 9.5))
    msp.add_text("DETALLE UNION CON PLACAS GANG-NAIL 1.5mm", dxfattribs={"layer": "A-TEXT", "height": 0.20}).set_placement((6.0, 5.0))

def _dibujar_red_alcantarillado(msp, plano):
    """Genera red sanitaria con tuberías PVC, pendientes y cámaras de inspección."""
    # Cámaras de inspección
    c1 = (16, 8)
    c2 = (11, 8)
    c3 = (6, 8)
    for cx, cy in [c1, c2, c3]:
        msp.add_circle((cx, cy), radius=0.4, dxfattribs={"layer": "MEP-SANI"})
        msp.add_circle((cx, cy), radius=0.3, dxfattribs={"layer": "MEP-SANI"})

    # Tubería principal colector
    msp.add_line(c3, c2, dxfattribs={"layer": "MEP-SANI"})
    msp.add_line(c2, c1, dxfattribs={"layer": "MEP-SANI"})
    msp.add_line(c1, (18, 8), dxfattribs={"layer": "MEP-SANI"}) # Hacia colector público

    # Ramales secundarios (Baño y Cocina)
    msp.add_line((6, 12), c3, dxfattribs={"layer": "MEP-SANI"})
    msp.add_line((11, 13), c2, dxfattribs={"layer": "MEP-SANI"})

    # Anotaciones técnicas RIDAA
    msp.add_text("C.I. N°1 (Cota Fondo: -0.85m)", dxfattribs={"layer": "A-TEXT", "height": 0.22}).set_placement((15.2, 8.8))
    msp.add_text("C.I. N°2 (Cota Fondo: -0.70m)", dxfattribs={"layer": "A-TEXT", "height": 0.22}).set_placement((10.2, 8.8))
    msp.add_text("C.I. N°3 (Cota Fondo: -0.55m)", dxfattribs={"layer": "A-TEXT", "height": 0.22}).set_placement((5.2, 8.8))
    msp.add_text("PVC SANITARIO D=110mm  i=3.0%", dxfattribs={"layer": "A-COTA", "height": 0.20}).set_placement((12.0, 7.3))
    msp.add_text("DESAGÜE COCINA PVC D=75mm i=2.5%", dxfattribs={"layer": "A-COTA", "height": 0.20}).set_placement((11.2, 11.0))
    msp.add_text("EMPALME A COLECTOR PUBLICO", dxfattribs={"layer": "A-TEXT", "height": 0.22}).set_placement((17.0, 9.2))

def _dibujar_red_electrica(msp, plano):
    """Genera trazado eléctrico, centros de luz, enchufes y tablero TDA."""
    # Tablero TDA
    msp.add_lwpolyline([(3, 9), (3.6, 9), (3.6, 9.8), (3, 9.8), (3, 9)], dxfattribs={"layer": "MEP-ELEC"})
    msp.add_text("T.D.A.", dxfattribs={"layer": "A-TEXT", "height": 0.22}).set_placement((2.8, 10.1))

    # Centros de luz
    centros = [(6, 13), (12, 13), (6, 7), (12, 7)]
    for pt in centros:
        msp.add_circle(pt, radius=0.35, dxfattribs={"layer": "MEP-ELEC"})
        msp.add_line((pt[0]-0.35, pt[1]), (pt[0]+0.35, pt[1]), dxfattribs={"layer": "MEP-ELEC"})
        msp.add_line((pt[0], pt[1]-0.35), (pt[0], pt[1]+0.35), dxfattribs={"layer": "MEP-ELEC"})

    # Curvas de canalización conduit
    msp.add_line((3.6, 9.4), centros[2], dxfattribs={"layer": "MEP-ELEC"})
    msp.add_line(centros[2], centros[3], dxfattribs={"layer": "MEP-ELEC"})
    msp.add_line(centros[2], centros[0], dxfattribs={"layer": "MEP-ELEC"})
    msp.add_line(centros[0], centros[1], dxfattribs={"layer": "MEP-ELEC"})

    msp.add_text("CIRCUITO 1: ALUMBRADO (1.5mm2 EVA / CONDUIT 20mm)", dxfattribs={"layer": "A-TEXT", "height": 0.22}).set_placement((4.0, 5.0))
    msp.add_text("CIRCUITO 2: ENCHUFES CON TIERRA (2.5mm2 EVA / CONDUIT 20mm)", dxfattribs={"layer": "A-TEXT", "height": 0.22}).set_placement((4.0, 4.3))

def _dibujar_fundaciones_estructura(msp, plano):
    """Genera planta de fundaciones corridas y zapatas."""
    # Ejes
    msp.add_line((3, 5), (16, 5), dxfattribs={"layer": "A-EJE"})
    msp.add_line((3, 14), (16, 14), dxfattribs={"layer": "A-EJE"})
    msp.add_line((5, 3), (5, 16), dxfattribs={"layer": "A-EJE"})
    msp.add_line((14, 3), (14, 16), dxfattribs={"layer": "A-EJE"})

    # Cimientos corridos de hormigón (ancho 50cm)
    msp.add_lwpolyline([(4.75, 4.75), (14.25, 4.75), (14.25, 14.25), (4.75, 14.25), (4.75, 4.75)], dxfattribs={"layer": "S-ESTR"})
    msp.add_lwpolyline([(5.25, 5.25), (13.75, 5.25), (13.75, 13.75), (5.25, 13.75), (5.25, 5.25)], dxfattribs={"layer": "S-ESTR"})

    # Zapatas en esquinas
    for zx in [5, 14]:
        for zy in [5, 14]:
            msp.add_lwpolyline([(zx-0.6, zy-0.6), (zx+0.6, zy-0.6), (zx+0.6, zy+0.6), (zx-0.6, zy+0.6), (zx-0.6, zy-0.6)], dxfattribs={"layer": "S-ESTR"})

    msp.add_text("CIMIENTO CORRIDO HORMIGÓN H20 (e=50cm h=80cm)", dxfattribs={"layer": "A-TEXT", "height": 0.24}).set_placement((4.0, 15.0))
    msp.add_text("ENFIERRADURA A63-42H SEGÚN CÁLCULO NCh433", dxfattribs={"layer": "A-TEXT", "height": 0.20}).set_placement((4.0, 3.5))

def _dibujar_corte_escantillon(msp, plano):
    """Genera corte escantillón con detalle de capas de aislamiento."""
    # Suelo / Terreno
    msp.add_line((3, 4), (15, 4), dxfattribs={"layer": "A-MURO"})
    # Sobrecimiento
    msp.add_lwpolyline([(5, 4), (5.4, 4), (5.4, 5.5), (5, 5.5), (5, 4)], dxfattribs={"layer": "S-ESTR"})
    # Muro envolvente
    msp.add_lwpolyline([(5.05, 5.5), (5.35, 5.5), (5.35, 14.0), (5.05, 14.0), (5.05, 5.5)], dxfattribs={"layer": "A-MURO"})
    # Alero y cubierta
    msp.add_line((4.2, 14.5), (7.0, 15.5), dxfattribs={"layer": "C-TECHO"})

    # Textos de capas técnicas
    msp.add_text("<- HOJALATERÍA ZINC-ALUM E=0.5mm", dxfattribs={"layer": "A-TEXT", "height": 0.20}).set_placement((7.2, 15.5))
    msp.add_text("<- MEMBRANA RESPIRABLE TIPO TYVEK", dxfattribs={"layer": "A-TEXT", "height": 0.20}).set_placement((6.0, 12.0))
    msp.add_text("<- LANA MINERAL 120mm (AISLACIÓN TÉRMICA)", dxfattribs={"layer": "A-TEXT", "height": 0.20}).set_placement((6.0, 10.5))
    msp.add_text("<- BARRERA DE VAPOR POLIETILENO 0.2mm", dxfattribs={"layer": "A-TEXT", "height": 0.20}).set_placement((6.0, 9.0))
    msp.add_text("<- PLACA YESO CARTÓN 15mm ST INTERIOR", dxfattribs={"layer": "A-TEXT", "height": 0.20}).set_placement((6.0, 7.5))
    msp.add_text("SOBRECIMIENTO HORMIGÓN ARMADO +0.30", dxfattribs={"layer": "A-TEXT", "height": 0.20}).set_placement((6.0, 5.0))

def _dibujar_topografia_emplazamiento(msp, plano):
    """Genera curvas de nivel y polígono de deslinde catastral."""
    # Curvas de nivel
    curvas = [
        [(3, 5), (6, 5.8), (10, 5.2), (15, 6)],
        [(3, 7.5), (7, 8.2), (11, 7.8), (15, 8.5)],
        [(3, 10), (6.5, 10.8), (10.5, 10.2), (15, 11)],
        [(3, 12.5), (7.5, 13.2), (11, 12.7), (15, 13.5)],
        [(3, 15), (7, 15.8), (12, 15.2), (15, 16)]
    ]
    cotas = ["+100.00 m", "+101.00 m", "+102.00 m", "+103.00 m", "+104.00 m"]
    for idx, c in enumerate(curvas):
        msp.add_lwpolyline(c, dxfattribs={"layer": "A-EJE"})
        msp.add_text(cotas[idx], dxfattribs={"layer": "A-COTA", "height": 0.18}).set_placement((15.2, c[-1][1]))

    # Polígono del sitio
    msp.add_lwpolyline([(4, 4), (14, 4), (14, 16.5), (4, 16.5), (4, 4)], dxfattribs={"layer": "A-MURO"})
    msp.add_text("POLÍGONO LOTE REGULADO (PRC)", dxfattribs={"layer": "A-TEXT", "height": 0.25}).set_placement((5.0, 17.0))

def _dibujar_geometria_generica(msp, plano):
    msp.add_lwpolyline([(4, 4), (16, 4), (16, 16), (4, 16), (4, 4)], dxfattribs={"layer": "A-MURO"})
    msp.add_text(plano.get("nombre", "PLANO"), dxfattribs={"layer": "A-TEXT", "height": 0.35}).set_placement((5, 10))

def exportar_memoria_tecnica(plano: dict, ruta_txt: str):
    """Genera documento de memoria técnica y cuadro de especificaciones."""
    contenido = f"""================================================================================
CHILEPLANOS - HUB DE PLANIMETRÍA ARQUITECTÓNICA Y DE INGENIERÍA
FICHA TÉCNICA Y ESPECIFICACIONES DE LÁMINA
================================================================================

DATOS GENERALES DEL PROYECTO:
--------------------------------------------------------------------------------
Código Documental:     {plano.get('codigo')}
Nombre del Plano:      {plano.get('nombre')}
Especialidad:          {plano.get('especialidad')}
Tipología:             {plano.get('tipologia')}
Ubicación / Región:    {plano.get('ubicacion')}
Escala Reglamentaria:  {plano.get('escala')}
Superficie / Alcance:  {plano.get('superficie')}
Formatos Suministrados: {plano.get('formato')}
Fuente / Repositorio:  {plano.get('fuente')}

DESCRIPCIÓN DEL PROYECTO:
--------------------------------------------------------------------------------
{plano.get('descripcion')}

ESPECIFICACIONES TÉCNICAS Y CRITERIOS DE NORMATIVA CHILENA:
--------------------------------------------------------------------------------
"""
    for idx, esp in enumerate(plano.get("especificaciones", []), 1):
        contenido += f"{idx}. {esp}\n"

    contenido += """
ESTÁNDARES CAD / BIM ASOCIADOS:
--------------------------------------------------------------------------------
- Capas (Layers): Según Directrices AIA (A-MURO, A-EJE, A-COTA, MEP-SANI, etc.)
- Sistema de Unidades: Metros (1 unidad dibujo = 1.0 metro)
- Compatible con: AutoCAD (.dwg/.dxf), Revit (.dwg/.ifc), ArchiCAD, LibreCAD.
================================================================================
"""
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta_txt
