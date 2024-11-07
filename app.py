import gradio as gr
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import os

# Funzione per aggiungere numeri di pagina senza perdere il contenuto
def add_page_numbers(pdf_file, position):
    # Legge il PDF caricato
    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    # Estrae il nome del file di input senza estensione
    input_filename = os.path.splitext(os.path.basename(pdf_file.name))[0]
    output_filename = f"{input_filename}_numerato.pdf"

    # Mappa le posizioni per il numero di pagina
    width, height = letter
    positions = {
        "In alto a destra": (width - 50, height - 9),
        "In alto a sinistra": (50, height - 9),
        "In alto al centro": (width / 2, height - 9),
        "In basso a destra": (width - 50, 9),
        "In basso a sinistra": (50, 9),
        "In basso al centro": (width / 2, 9),
    }
    x, y = positions.get(position, (width - 50, height - 30))

    # Itera sulle pagine e crea una sovrapposizione con i numeri di pagina
    for i, page in enumerate(reader.pages, start=1):
        # Crea un file temporaneo per l'overlay della pagina
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as overlay_pdf:
            overlay_file = overlay_pdf.name
        
        # Usa ReportLab per creare l'overlay
        c = canvas.Canvas(overlay_file, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(x, y, str(i))  # Scrive il numero della pagina nella posizione scelta
        c.save()
        
        # Legge l'overlay appena creato
        overlay_reader = PdfReader(overlay_file)
        overlay_page = overlay_reader.pages[0]

        # Unisce l'overlay con la pagina originale
        page.merge_page(overlay_page)
        writer.add_page(page)

    # Crea il file di output con il nome desiderato
    output_file_path = os.path.join(tempfile.gettempdir(), output_filename)
    with open(output_file_path, "wb") as f:
        writer.write(f)

    return output_file_path

# Crea l'interfaccia grafica con Gradio
interface = gr.Interface(
    fn=add_page_numbers,
    inputs=[
        gr.File(label="Carica il tuo PDF"),
        gr.Dropdown(
            ["In alto a destra", "In alto a sinistra", "In alto al centro",
             "In basso a destra", "In basso a sinistra", "In basso al centro"],
            label="Posizione del numero di pagina"
        )
    ],
    outputs=gr.File(label="Scarica il PDF numerato"),
    title="Numera il tuo PDF"
)

# Avvia l'interfaccia
interface.launch()
