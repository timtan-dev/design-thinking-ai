"""
File Processor Service
Handle file uploads and processing
"""

import os
from pathlib import Path
from config.settings import Settings
from typing import Optional
import csv
import PyPDF2
from docx import Document

def save_uploaded_file(uploaded_file, project_id: int, method_type: str = "general") -> Optional[str]:
    """
    Save uploaded file to disk

    Args:
        uploaded_file: Streamlit uploaded file object
        project_id: Project ID
        method_type: Type of research method

    Returns:
        File path if successful, None otherwise
    """
    try:
        # Create project directory
        project_dir = Settings.UPLOAD_DIR / str(project_id) / method_type
        project_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = project_dir / uploaded_file.name
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        return str(file_path)

    except Exception as e:
        print(f"Error saving file: {str(e)}")
        return None

def read_csv_file(file_path: str) -> list:
    """
    Read CSV file and return data

    Args:
        file_path: Path to CSV file

    Returns:
        List of dictionaries containing CSV data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return []

def read_txt_file(file_path: str) -> str:
    """
    Read text file

    Args:
        file_path: Path to text file

    Returns:
        File contents as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading text file: {str(e)}")
        return ""

def read_pdf_file(file_path: str) -> str:
    """
    Read PDF file and extract text

    Args:
        file_path: Path to PDF file

    Returns:
        Extracted text
    """
    try:
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        return ""

def read_docx_file(file_path: str) -> str:
    """
    Read DOCX file and extract text

    Args:
        file_path: Path to DOCX file

    Returns:
        Extracted text
    """
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading DOCX: {str(e)}")
        return ""

def process_uploaded_file(file_path: str) -> dict:
    """
    Process uploaded file based on type

    Args:
        file_path: Path to uploaded file

    Returns:
        Dictionary with file content and metadata
    """
    file_ext = Path(file_path).suffix.lower()

    if file_ext == '.csv':
        content = read_csv_file(file_path)
        content_type = 'csv'
    elif file_ext == '.txt':
        content = read_txt_file(file_path)
        content_type = 'text'
    elif file_ext == '.pdf':
        content = read_pdf_file(file_path)
        content_type = 'text'
    elif file_ext in ['.docx', '.doc']:
        content = read_docx_file(file_path)
        content_type = 'text'
    else:
        content = None
        content_type = 'unknown'

    return {
        'content': content,
        'type': content_type,
        'file_name': Path(file_path).name,
        'file_path': file_path
    }
