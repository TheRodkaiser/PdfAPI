
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from reportlab.pdfgen import canvas
from io import BytesIO
from pdf2docx import Converter
from docx2pdf import convert
import ocrmypdf
from PIL import Image
from pdf2image import convert_from_path
import os
import pdfkit



def merge_pdfs(pdf_list, output_path):
    """
    Une varios archivos PDF en uno solo.
    
    :param pdf_list: Lista de rutas de archivos PDF a unir.
    :param output_path: Ruta del archivo PDF de salida.
    """
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()

def split_pdf(input_pdf, output_pdf, pages):
    """
    Extrae páginas específicas de un PDF y las guarda en un nuevo archivo.
    
    :param input_pdf: Ruta del PDF de origen.
    :param output_pdf: Ruta del PDF resultante.
    :param pages: Lista de índices de páginas a extraer (0-indexado).
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    for page_num in pages:
        writer.add_page(reader.pages[page_num])
    with open(output_pdf, 'wb') as f:
        writer.write(f)

def pdf_to_word(pdf_path, docx_path):
    """
    Convierte un archivo PDF a un documento Word (.docx).
    
    :param pdf_path: Ruta del PDF de origen.
    :param docx_path: Ruta del archivo Word de salida.
    """
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()


def ocr_pdf(input_pdf, output_pdf):
    """
    Aplica OCR a un PDF, generando un archivo PDF buscable.
    
    :param input_pdf: Ruta del PDF original.
    :param output_pdf: Ruta del PDF resultante con OCR.
    """
    # El parámetro deskew corrige la inclinación si es necesario.
    ocrmypdf.ocr(input_pdf, output_pdf, deskew=True)

def word_to_pdf(docx_path, pdf_path):
    """
    Convierte un documento Word a PDF.
    
    :param docx_path: Ruta del archivo Word.
    :param pdf_path: Ruta del archivo PDF de salida.
    """
    convert(docx_path, pdf_path)


def image_to_pdf(image_path, pdf_path):
    """
    Convierte una imagen (JPG o PNG) a PDF.
    
    :param image_path: Ruta de la imagen de origen.
    :param pdf_path: Ruta del PDF de salida.
    """
    image = Image.open(image_path)
    # Convertir a RGB si la imagen tiene transparencia u otro modo
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(pdf_path, "PDF", resolution=100.0)


def pdf_to_images(pdf_path, output_folder):
    """
    Convierte cada página de un PDF a una imagen JPEG.
    
    :param pdf_path: Ruta del PDF de origen.
    :param output_folder: Carpeta donde se guardarán las imágenes.
    :return: Lista de rutas de las imágenes generadas.
    """
    pages = convert_from_path(pdf_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    image_paths = []
    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f"page_{i+1}.jpg")
        page.save(image_path, "JPEG")
        image_paths.append(image_path)
    return image_paths


def create_signature_overlay(signature_image, page_width, page_height, x, y, width=100, height=50):
    """
    Crea un overlay PDF con la imagen de firma en la posición indicada.
    
    :param signature_image: Ruta de la imagen de la firma.
    :param page_width: Ancho de la página.
    :param page_height: Alto de la página.
    :param x: Posición X donde se colocará la firma.
    :param y: Posición Y donde se colocará la firma.
    :param width: Ancho de la imagen de la firma en el overlay.
    :param height: Alto de la imagen de la firma en el overlay.
    :return: Página del overlay como objeto de PyPDF2.
    """
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
    can.drawImage(signature_image, x, y, width=width, height=height, mask='auto')
    can.save()
    packet.seek(0)
    from PyPDF2 import PdfReader
    overlay_pdf = PdfReader(packet)
    return overlay_pdf.pages[0]

def sign_pdf(input_pdf, signature_image, output_pdf, page_number=0, x=100, y=100, width=100, height=50):
    """
    Inserta una imagen de firma en una página específica del PDF.
    
    :param input_pdf: Ruta del PDF original.
    :param signature_image: Ruta de la imagen de la firma.
    :param output_pdf: Ruta del PDF firmado.
    :param page_number: Índice (0-indexado) de la página donde se insertará la firma.
    :param x: Posición X para la firma.
    :param y: Posición Y para la firma.
    :param width: Ancho de la firma.
    :param height: Alto de la firma.
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    target_page = reader.pages[page_number]
    overlay = create_signature_overlay(signature_image, float(target_page.mediabox.width),
                                         float(target_page.mediabox.height), x, y, width, height)
    target_page.merge_page(overlay)
    # Agregar todas las páginas (con la firmada reemplazada)
    for i, page in enumerate(reader.pages):
        if i == page_number:
            writer.add_page(target_page)
        else:
            writer.add_page(page)
    with open(output_pdf, 'wb') as f:
        writer.write(f)


def add_watermark(input_pdf, watermark_pdf, output_pdf):
    """
    Añade una marca de agua (proporcionada como un PDF de una sola página) a todas las páginas de un PDF.
    
    :param input_pdf: Ruta del PDF original.
    :param watermark_pdf: Ruta del PDF que contiene la marca de agua (normalmente de una sola página).
    :param output_pdf: Ruta del PDF resultante con la marca de agua.
    """
    reader_pdf = PdfReader(input_pdf)
    reader_watermark = PdfReader(watermark_pdf)
    watermark_page = reader_watermark.pages[0]
    writer = PdfWriter()
    for page in reader_pdf.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
    with open(output_pdf, 'wb') as f:
        writer.write(f)



def html_to_pdf(html_path, output_pdf):
    """
    Convierte un archivo HTML a PDF.
    
    :param html_path: Ruta del archivo HTML.
    :param output_pdf: Ruta del PDF de salida.
    """
    pdfkit.from_file(html_path, output_pdf)


