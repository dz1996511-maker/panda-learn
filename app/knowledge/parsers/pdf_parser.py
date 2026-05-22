import os
import subprocess
import tempfile


def parse_pdf(content: bytes) -> str:
    """Parse PDF content using pdftotext (poppler), fallback to PyMuPDF."""

    # 首选：pdftotext（中文支持更好）
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            pdf_path = tmp.name

        txt_path = pdf_path + ".txt"
        result = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", pdf_path, txt_path],
            capture_output=True, timeout=30,
        )

        if result.returncode == 0 and os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            os.unlink(pdf_path)
            os.unlink(txt_path)
            if text.strip():
                return text

        # Cleanup on failure
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
        if os.path.exists(txt_path):
            os.unlink(txt_path)
    except Exception:
        # pdftotext 失败，继续用 PyMuPDF
        pass

    # 备选：PyMuPDF
    import fitz
    doc = fitz.open(stream=content, filetype="pdf")
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts)
