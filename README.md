# ChilePlanos 📐🏛️

Hub de Planimetría Técnica y Arquitectura para estudiantes desarrollado en **Python Puro** con interfaz moderna nativa (**CustomTkinter**) y empaquetado para Windows mediante **PyInstaller (`ChilePlanos.spec`)**.

---

## 🎯 Características para Estudiantes de Arquitectura

- **Catálogo Técnico Especializado:**
  - **Arquitectura:** Plantas de distribución, ejes, cuadros de vanos y cotas.
  - **Techumbre:** Cerchas de pino radiata, limahoyas, hojalatería y cálculo de pendientes (NCh431/432).
  - **Alcantarillado & Sanitario:** Trazados de PVC sanitario clase 4 (110/75mm), cámaras y cuadros de U.E.H. (RIDAA / SISS).
  - **Eléctrico:** Circuitos de alumbrado y fuerza, tableros TDA y cumplimiento de la norma SEC (Pliego RIC N°10).
  - **Estructural:** Fundaciones corridas, vigas y armaduras de hormigón armado bajo norma sísmica NCh433.
  - **Detalles Constructivos:** Cortes escantillón y roturas de puente térmico para Planes de Descontaminación Atmosférica (PDA).
  - **Planimetría General:** Curvas de nivel, loteos y cotas de terreno.
- **Geodatos & Topografía API:**
  - Conexión con **Overpass API (OpenStreetMap)** para descargar geometrías y polígonos de edificaciones y vías de ciudades chilenas para importar en programas CAD/BIM.
- **Sin dependencias pesadas de navegador:** Ejecutable nativo, rápido y con mínimo consumo de memoria RAM.

---

## 💻 Desarrollo y Ejecución Local

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar la aplicación:
   ```bash
   python main.py
   ```
3. Compilar el ejecutable localmente con el archivo `.spec`:
   ```bash
   pyinstaller --clean ChilePlanos.spec
   ```
   El archivo ejecutable `ChilePlanos.exe` quedará listo en la carpeta `dist/`.

---

## 🚀 Compilación y Releases Automáticos en GitHub Actions

El flujo en `.github/workflows/release.yml` utiliza `ChilePlanos.spec` para compilar el ejecutable en una máquina Windows virtual limpia.

Para publicar una nueva versión con el `.exe` listo para descargar:

```bash
git tag v1.0.1
git push origin v1.0.1
```

GitHub Actions compilará `dist/ChilePlanos.exe` y creará la release automáticamente adjuntando el instalador/ejecutable.
