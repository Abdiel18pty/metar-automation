import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from docx import Document
import os

# ================= CONFIG =================
ICAOS = ["MPTO", "MPMG", "MPPA", "MPSM", "MPDA", "MPBO"]
BASE_DIR = "METAR"
TIMEZONE = ZoneInfo("America/Panama")

URL_NOAA = (
    "https://aviationweather.gov/data/metar/"
    "?ids=" + ",".join(ICAOS)
)
# =========================================


def obtener_metars_noaa():
    r = requests.get(URL_NOAA, timeout=30)
    r.raise_for_status()
    return [
        m.strip() for m in r.text.splitlines()
        if len(m.strip()) > 20
    ]


def archivo_diario():
    fecha = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    os.makedirs(BASE_DIR, exist_ok=True)
    return os.path.join(BASE_DIR, f"METAR_{fecha}.docx")


def cargar_existentes(doc):
    return {p.text.strip() for p in doc.paragraphs if p.text.strip()}


def main():
    archivo = archivo_diario()

    doc = Document(archivo) if os.path.exists(archivo) else Document()
    existentes = cargar_existentes(doc)

    metars = set(obtener_metars_noaa())

    nuevos = sorted(metars - existentes)

    if nuevos:
        if not existentes:
            doc.add_heading("METAR DIARIOS – PANAMÁ", level=1)

        for metar in nuevos:
            doc.add_paragraph(metar)

        doc.save(archivo)

    print(
        f"[OK] {len(nuevos)} METAR nuevos | "
        f"{datetime.now(TIMEZONE)}"
    )


if __name__ == "__main__":
    main()
