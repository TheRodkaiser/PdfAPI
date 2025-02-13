import os
import shutil
import tempfile
import zipfile
from io import BytesIO
from typing import List
import funciones as fn

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse


app = FastAPI(title="API de Procesamiento de Documentos")

# ---------------- Función para eliminar archivos temporales ----------------

def remove_file(path: str):
    try:
        os.remove(path)
    except Exception as e:
        print(f"Error al eliminar {path}: {e}")


# ---------------- Endpoints del API ----------------

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a la API de procesamiento de documentos."}


@app.post("/merge_pdfs")
async def api_merge_pdfs(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Une múltiples PDFs y devuelve el PDF resultante.
    """
    temp_files = []
    try:
        # Guardar cada PDF en un archivo temporal
        for file in files:
            suffix = os.path.splitext(file.filename)[1] or ".pdf"
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            content = await file.read()
            temp.write(content)
            temp.close()
            temp_files.append(temp.name)
        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_temp.close()
        fn.merge_pdfs(temp_files, output_temp.name)
        # Programar limpieza
        for temp_path in temp_files:
            background_tasks.add_task(remove_file, temp_path)
        background_tasks.add_task(remove_file, output_temp.name)
        return FileResponse(output_temp.name, media_type="application/pdf", filename="merged.pdf")
    except Exception as e:
        return {"error": str(e)}


@app.post("/split_pdf")
async def api_split_pdf(
    file: UploadFile = File(...),
    pages: str = Form(...),
    background_tasks: BackgroundTasks = None
):
    """
    Extrae páginas específicas de un PDF.
    El parámetro 'pages' debe ser una cadena separada por comas (por ejemplo: "0,2,3").
    """
    try:
        suffix = os.path.splitext(file.filename)[1] or ".pdf"
        temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        content = await file.read()
        temp_in.write(content)
        temp_in.close()
        # Convertir la cadena de páginas a lista de enteros
        pages_list = [int(p.strip()) for p in pages.split(",")]
        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_temp.close()
        fn.split_pdf(temp_in.name, output_temp.name, pages_list)
        background_tasks.add_task(remove_file, temp_in.name)
        background_tasks.add_task(remove_file, output_temp.name)
        return FileResponse(output_temp.name, media_type="application/pdf", filename="split.pdf")
    except Exception as e:
        return {"error": str(e)}


@app.post("/pdf_to_word")
async def api_pdf_to_word(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Convierte un PDF a un documento Word (.docx).
    """
    try:
        suffix = os.path.splitext(file.filename)[1] or ".pdf"
        temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        content = await file.read()
        temp_in.write(content)
        temp_in.close()
        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        output_temp.close()
        fn.pdf_to_word(temp_in.name, output_temp.name)
        background_tasks.add_task(remove_file, temp_in.name)
        background_tasks.add_task(remove_file, output_temp.name)
        return FileResponse(
            output_temp.name,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="converted.docx"
        )
    except Exception as e:
        return {"error": str(e)}


@app.post("/ocr_pdf")
async def api_ocr_pdf(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Aplica OCR a un PDF para hacerlo buscable.
    """
    try:
        suffix = os.path.splitext(file.filename)[1] or ".pdf"
        temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        content = await file.read()
        temp_in.write(content)
        temp_in.close()
        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_temp.close()
        fn.ocr_pdf(temp_in.name, output_temp.name)
        background_tasks.add_task(remove_file, temp_in.name)
        background_tasks.add_task(remove_file, output_temp.name)
        return FileResponse(output_temp.name, media_type="application/pdf", filename="ocr.pdf")
    except Exception as e:
        return {"error": str(e)}


@app.post("/word_to_pdf")
async def api_word_to_pdf(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Convierte un documento Word a PDF.
    """
    try:
        suffix = os.path.splitext(file.filename)[1] or ".docx"
        temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        content = await file.read()
        temp_in.write(content)
        temp_in.close()
        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_temp.close()
        fn.word_to_pdf(temp_in.name, output_temp.name)
        background_tasks.add_task(remove_file, temp_in.name)
        background_tasks.add_task(remove_file, output_temp.name)
        return FileResponse(output_temp.name, media_type="application/pdf", filename="word_converted.pdf")
    except Exception as e:
        return {"error": str(e)}


@app.post("/image_to_pdf")
async def api_image_to_pdf(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Convierte una imagen (JPG o PNG) a PDF.
    """
    try:
        suffix = os.path.splitext(file.filename)[1] or ".png"
        temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        content = await file.read()
        temp_in.write(content)
        temp_in.close()
        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_temp.close()
        fn.image_to_pdf(temp_in.name, output_temp.name)
        background_tasks.add_task(remove_file, temp_in.name)
        background_tasks.add_task(remove_file, output_temp.name)
        return FileResponse(output_temp.name, media_type="application/pdf", filename="image_converted.pdf")
    except Exception as e:
        return {"error": str(e)}


@app.post("/pdf_to_images")
async def api_pdf_to_images(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Convierte cada página de un PDF a imágenes JPEG y las devuelve empaquetadas en un ZIP.
    """
    try:
        suffix = os.path.splitext(file.filename)[1] or ".pdf"
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        content = await file.read()
        temp_pdf.write(content)
        temp_pdf.close()
        
        # Directorio temporal para guardar las imágenes
        temp_dir = tempfile.mkdtemp()
        image_paths = fn.pdf_to_images(temp_pdf.name, temp_dir)
        
        zip_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        zip_temp.close()
        with zipfile.ZipFile(zip_temp.name, 'w') as zipf:
            for img_path in image_paths:
                zipf.write(img_path, arcname=os.path.basename(img_path))
        
        # Programar limpieza de archivos temporales
        background_tasks.add_task(remove_file, temp_pdf.name)
        background_tasks.add_task(shutil.rmtree, temp_dir)
        background_tasks.add_task(remove_file, zip_temp.name)
        return FileResponse(zip_temp.name, media_type="application/zip", filename="images.zip")
    except Exception as e:
        return {"error": str(e)}


@app.post("/sign_pdf")
async def api_sign_pdf(
    file: UploadFile = File(...),
    signature: UploadFile = File(...),
    page_number: int = Form(0),
    x: float = Form(100),
    y: float = Form(100),
    width: float = Form(100),
    height: float = Form(50),
    background_tasks: BackgroundTasks = None
):
    """
    Inserta una imagen de firma en una página específica del PDF.
    """
    try:
        pdf_suffix = os.path.splitext(file.filename)[1] or ".pdf"
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=pdf_suffix)
        content = await file.read()
        temp_pdf.write(content)
        temp_pdf.close()

        img_suffix = os.path.splitext(signature.filename)[1] or ".png"
        temp_sig = tempfile.NamedTemporaryFile(delete=False, suffix=img_suffix)
        sig_content = await signature.read()
        temp_sig.write(sig_content)
        temp_sig.close()

        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_temp.close()

        fn.sign_pdf(temp_pdf.name, temp_sig.name, output_temp.name, page_number, x, y, width, height)
        background_tasks.add_task(remove_file, temp_pdf.name)
        background_tasks.add_task(remove_file, temp_sig.name)
        background_tasks.add_task(remove_file, output_temp.name)
        return FileResponse(output_temp.name, media_type="application/pdf", filename="signed.pdf")
    except Exception as e:
        return {"error": str(e)}


@app.post("/add_watermark")
async def api_add_watermark(
    file: UploadFile = File(...),
    watermark: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Añade una marca de agua (proporcionada como un PDF de una sola página) a todas las páginas del PDF.
    """
    try:
        pdf_suffix = os.path.splitext(file.filename)[1] or ".pdf"
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=pdf_suffix)
        content = await file.read()
        temp_pdf.write(content)
        temp_pdf.close()

        watermark_suffix = os.path.splitext(watermark.filename)[1] or ".pdf"
        temp_watermark = tempfile.NamedTemporaryFile(delete=False, suffix=watermark_suffix)
        w_content = await watermark.read()
        temp_watermark.write(w_content)
        temp_watermark.close()

        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_temp.close()

        fn.add_watermark(temp_pdf.name, temp_watermark.name, output_temp.name)
        background_tasks.add_task(remove_file, temp_pdf.name)
        background_tasks.add_task(remove_file, temp_watermark.name)
        background_tasks.add_task(remove_file, output_temp.name)
        return FileResponse(output_temp.name, media_type="application/pdf", filename="watermarked.pdf")
    except Exception as e:
        return {"error": str(e)}


@app.post("/html_to_pdf")
async def api_html_to_pdf(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Convierte un archivo HTML a PDF.
    """
    try:
        html_suffix = os.path.splitext(file.filename)[1] or ".html"
        temp_html = tempfile.NamedTemporaryFile(delete=False, suffix=html_suffix)
        content = await file.read()
        temp_html.write(content)
        temp_html.close()

        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_temp.close()

        fn.html_to_pdf(temp_html.name, output_temp.name)
        background_tasks.add_task(remove_file, temp_html.name)
        background_tasks.add_task(remove_file, output_temp.name)
        return FileResponse(output_temp.name, media_type="application/pdf", filename="converted.pdf")
    except Exception as e:
        return {"error": str(e)}
