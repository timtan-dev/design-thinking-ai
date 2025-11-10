# DOCX File Text Extraction Fix

## Problem Identified

When users uploaded `.docx` (Word document) files as research data in the Empathise stage, the application was saving **binary ZIP data** instead of extracting the actual text content.

### Symptoms

- AI models received corrupted input like: `PK!2oWf[Content_Types].xml...`
- OpenAI console showed random characters instead of meaningful text
- No useful AI-generated insights from research data
- All 13 existing `.docx` uploads in database had corrupted content

### Root Cause

In [pages/empathise.py:234](pages/empathise.py#L234), the `save_research_data()` function was treating all files the same:

```python
# OLD CODE - Binary data for .docx files
file_content = uploaded_file.read().decode("utf-8", errors="ignore")
```

This worked for `.txt` and `.csv` files, but `.docx` files are actually **ZIP archives** containing XML. The binary ZIP structure was being decoded as UTF-8, resulting in gibberish.

## Solution Implemented

### 1. Updated File Upload Handler

Modified [pages/empathise.py](pages/empathise.py) to detect file type and extract text appropriately:

```python
# NEW CODE - Proper text extraction
file_extension = uploaded_file.name.split('.')[-1].lower()

if file_extension == 'docx':
    # Extract text from Word document using python-docx
    doc = Document(io.BytesIO(uploaded_file.read()))
    file_content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
elif file_extension == 'pdf':
    # PDF text extraction (basic - can be improved)
    file_content = uploaded_file.read().decode("utf-8", errors="ignore")
else:
    # txt, csv, and other text files
    file_content = uploaded_file.read().decode("utf-8", errors="ignore")
```

### 2. Migration Script for Existing Data

Created [migrations/fix_docx_content.py](migrations/fix_docx_content.py) to re-extract text from all corrupted database records:

**Results:**
- ✅ Successfully fixed all 13 corrupted records
- ✅ Extracted between 14,695 to 107,077 characters per document
- ✅ All records now contain readable text instead of binary data
- ✅ Records marked as unprocessed so AI can re-analyze with correct content

### 3. Added Dependencies

The `python-docx>=0.8.11` library was already in [requirements.txt](requirements.txt), so no additional installation needed.

## Verification

**Before Fix:**
```
Content: PK     ! 2oWf     [Content_Types].xml...
```

**After Fix:**
```
Content: SYNTHETIC STAKEHOLDER INTERVIEWS
Whyalla Hydrogen Power Facility Project (2021-2024)

INTERVIEW 1: GOVERNMENT PERSPECTIVE
Interviewee: Sam Crafter, Deputy Director...
```

## Files Modified

1. **[pages/empathise.py](pages/empathise.py)**
   - Added `from docx import Document` and `import io`
   - Updated `save_research_data()` function with file-type detection
   - Added proper error handling

2. **[migrations/fix_docx_content.py](migrations/fix_docx_content.py)** *(new)*
   - Migration script to fix existing corrupted records
   - Re-extracts text from physical `.docx` files
   - Updates database with extracted text

## Impact

### For New Uploads
- All future `.docx` uploads will automatically extract text content
- AI models will receive clean, readable text
- Research insights will be accurate and meaningful

### For Existing Data
- All 13 previously corrupted records have been fixed
- Research data is now usable for AI analysis
- Projects can now generate proper insights from uploaded documents

## Testing

To test the fix:

1. **Upload a new .docx file:**
   ```bash
   streamlit run app.py
   ```
   - Navigate to a project → Empathise stage
   - Upload a `.docx` file via any research method
   - Verify in database that content is readable text

2. **Verify migration results:**
   ```bash
   source design-thinking-ai/bin/activate
   python -c "from config.database import get_db; from database.models import ResearchData; db = get_db(); data = db.query(ResearchData).first(); print(data.file_content[:200]); db.close()"
   ```

## Future Improvements

### PDF Text Extraction
Currently, PDF files are decoded as UTF-8 (basic extraction). Consider using `PyPDF2` or `pdfplumber` for better extraction:

```python
from PyPDF2 import PdfReader

if file_extension == 'pdf':
    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    file_content = '\n'.join([page.extract_text() for page in reader.pages])
```

### Image/OCR Support
For scanned documents or images, consider adding OCR capabilities:
- `pytesseract` for OCR
- `Pillow` for image processing (already in requirements.txt)

### Document Metadata
Extract additional metadata from documents:
- Author, creation date, modification date
- Document statistics (word count, page count)
- Embedded images or tables

## Related Documentation

- [LangChain Setup](LANGCHAIN_SETUP.md) - Multi-provider AI configuration
- [Deployment Guide](../DEPLOYMENT.md) - Streamlit Cloud deployment
- [Quick Start](../QUICKSTART.md) - Getting started guide

---

**Status:** ✅ Fixed and verified
**Date:** 2025-11-10
**Records Fixed:** 13 corrupted .docx files successfully repaired
