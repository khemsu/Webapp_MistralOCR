import streamlit as st
import base64
import os
import io
import re
import fitz
import pdfplumber
from PIL import Image
from mistralai import Mistral
from dotenv import load_dotenv
import easyocr
import numpy as np

# Load API key
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)
easyocr_reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_pdf_plumber(file):
    with pdfplumber.open(file) as pdf:
        text = pdf.pages[0].extract_text()
    return text

def is_scanned_pdf(file):
    try:
        file.seek(0)
        with pdfplumber.open(file) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            if not text or len(text.strip()) < 50:
                return True
    except Exception:
        return True
    return False

def convert_pdf_page_to_image(file):
    file.seek(0)
    pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
    page = pdf_doc.load_page(0)
    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return img

def encode_image(image):
    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format="PNG") 
    base64_encoded = base64.b64encode(img_byte_array.getvalue()).decode("utf-8")
    return base64_encoded

def extract_text_from_image(image):
    base64_image = encode_image(image)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Below is the image of one page of a document. Return the plain text representation as naturally as possible."},
                {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}
            ]
        }
    ]
    try:
        response = client.chat.complete(model="mistral-small-latest", messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def extract_text_with_easyocr(image):
    image_np = np.array(image)
    results = easyocr_reader.readtext(image_np, detail=0)
    return "\n".join(results)

def extract_structured_text(plain_text):
    extraction_prompt = f"""
You are an expert document parser specializing in commercial documents like invoices, bills, and insurance papers.

Extract the following structured data from the document text:
- vendor_details: name, address, phone, email, website, PAN
- customer_details: name, address, contact, PAN (usually below vendor_details)
- invoice_details: bill_number, bill_date, transaction_date, mode_of_payment, finance_manager, authorized_signatory
- payment_details: total, in_words, discount, taxable_amount, vat, net_amount
- line_items (list): hs_code, description, qty, rate, amount

Rules:
1. Extract only the fields listed; do not guess or add extra fields.
2. If a field is missing, set its value as null.
3. Use context ('Vendor', 'Supplier', 'Bill To', 'Customer', etc.) to distinguish parties. If unclear, the first business is Vendor, the second is Customer.
4. Each line_item must include hs_code and description; qty, rate, and amount are optional.
5. Always return the result strictly in the following JSON structure.
6. PAN numbers are typically boxed or near labels like 'PAN No.', and follow a 9-digit (Nepal) format.

Return the structured data using this exact JSON format:

{{
  "vendor_details": {{
    "name": "...",
    "address": "...", 
    "phone": "...", 
    "email": "...",
    "website": "...",
    "pan": "..."
  }},
  "customer_details": {{
    "name": "...",
    "address": "...",
    "contact": "...",
    "pan": "..."
  }},
  "invoice_details": {{
    "bill_number": "...",
    "bill_date": "...",
    "transaction_date": "...",
    "mode_of_payment": "...",
    "finance_manager": "...",
    "authorized_signatory": "..."
  }},
  "payment_details": {{
    "total": 0,
    "in_words": "...",
    "discount": 0,
    "taxable_amount": 0,
    "vat": 0,
    "net_amount": 0
  }},
  "line_items": [
    {{
      "hs_code": "...",
      "particulars": "...",
      "qty": "...",
      "rate": "...",
      "amount": "..."
    }}
  ]
}}

Text:
\"\"\"
{plain_text}
\"\"\"

Important: Return ONLY the JSON object. No explanations, no headings, no extra text.
"""
    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": extraction_prompt}]
        )
        raw = response.choices[0].message.content
        cleaned = re.sub(r"^```(?:json)?\s*|```$", "", raw.strip(), flags=re.MULTILINE)
        return cleaned
    except Exception as e:
        return f"Error during structured extraction: {str(e)}"


st.title("Document Extractor (PDF or Image)")

uploaded_file = st.file_uploader("Upload a document (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    file_type = uploaded_file.type
    with st.spinner("Analyzing document..."):
        if file_type == "application/pdf":
            if is_scanned_pdf(uploaded_file):
                st.info("Scanned PDF detected. Using OCR.")
                image = convert_pdf_page_to_image(uploaded_file)
                plain_text = extract_text_from_image(image)
            else:
                st.info("Digital PDF detected. Extracting text.")
                uploaded_file.seek(0)
                plain_text = extract_text_from_pdf_plumber(uploaded_file)
        elif "image" in file_type:
            st.info("Image detected. Using EasyOCR.")
            image = Image.open(uploaded_file)
            plain_text = extract_text_with_easyocr(image)
        else:
            plain_text = "Unsupported file format."

    st.subheader("Extracted Raw Text")
    st.text_area("Raw Text", plain_text, height=800)

    if st.button("Extract Structured Data"):
        structured_data = extract_structured_text(plain_text)
        st.subheader("Structured Data")
        st.json(structured_data)

