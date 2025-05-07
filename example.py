# # if uploaded_file is not None:
# #     image = Image.open(uploaded_file)
# #     st.image(image, caption="Uploaded Image", use_column_width=True)

# #     if st.button("Extract Raw Text"):
# #         with st.spinner("Extracting raw text..."):
# #             plain_text = extract_text_from_image(image)
# #             extracted_text = extract_structured_text(plain_text)
        
# #         st.subheader("Extracted raw Text:")
# #         st.text_area("OCR Output", plain_text, height=800)

# #         st.subheader("Extracted structured Text:")
# #         st.text_area("OCR Output", extracted_text, height=800)



# previous
# import streamlit as st
# import base64
# import requests
# import os
# from mistralai import Mistral
# from dotenv import load_dotenv
# from PIL import Image
# import io
# import pdfplumber
# import re

# # Load API key from .env file
# load_dotenv()
# api_key = os.getenv("MISTRAL_API_KEY")

# # Initialize Mistral AI client
# client = Mistral(api_key=api_key)

# def extract_text_from_pdf_plumber(file):
#     """Extract text from PDF using pdfplumber."""
#     with pdfplumber.open(file) as pdf:
#         full_text = ""
#         # Extract text from the first page
#         first_page = pdf.pages[0]
#         full_text = first_page.extract_text()  # Extract text from the first page
#     return full_text

# def encode_image(image):
#     """Encode an uploaded image to base64."""
#     img_byte_array = io.BytesIO()
#     image.save(img_byte_array, format="PNG") 
#     base64_encoded = base64.b64encode(img_byte_array.getvalue()).decode("utf-8")
#     return base64_encoded

# def extract_text_from_image(image):
#     """Send the image to Mistral AI OCR and extract text."""
#     base64_image = encode_image(image)
    
#     messages = [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "Below is the image of one page of a document, as well as some raw textual content that was previously extracted for it. Just return the plain text representation of this document as if you were reading it naturally. Do not hallucinate."
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": f"data:image/png;base64,{base64_image}"
#                 }
#             ]
#         }
#     ]
    
#     model = "mistral-small-latest"

#     try:
#         chat_response = client.chat.complete(model=model, messages=messages)
#         return chat_response.choices[0].message.content
#     except Exception as e:
#         return f"Error: {str(e)}"
    
# def extract_structured_text(plain_text):
#     """Extract structured information like vendor, customer, items from text."""
#     extraction_prompt = f"""
# You are an expert document parser specializing in commercial documents like invoices, bills, and insurance papers.

# Extract the following structured data from the document text:
# - vendor_details: name, address, phone, email, website, PAN
# - customer_details: name, address, contact, PAN (usually below vendor_details)
# - invoice_details: bill_number, bill_date, transaction_date, mode_of_payment, finance_manager, authorized_signatory
# - payment_details: total, in_words, discount, taxable_amount, vat, net_amount
# - line_items (list): hs_code, description, qty, rate, amount

# Rules:
# 1. Extract only the fields listed; do not guess or add extra fields.
# 2. If a field is missing, set its value as null.
# 3. Use context ('Vendor', 'Supplier', 'Bill To', 'Customer', etc.) to distinguish parties. If unclear, the first business is Vendor, the second is Customer.
# 4. Each line_item must include hs_code and description; qty, rate, and amount are optional.
# 5. Always return the result strictly in the following JSON structure.
# 6. PAN numbers are typically boxed or near labels like 'PAN No.', and follow a 9-digit (Nepal) format.

# Return the structured data using this exact JSON format:

# {{
#   "vendor_details": {{
#     "name": "...",
#     "address": "...", 
#     "phone": "...", 
#     "email": "...",
#     "website": "...",
#     "pan": "..."
#   }},
#   "customer_details": {{
#     "name": "...",
#     "address": "...",
#     "contact": "...",
#     "pan": "..."
#   }},
#   "invoice_details": {{
#     "bill_number": "...",
#     "bill_date": "...",
#     "transaction_date": "...",
#     "mode_of_payment": "...",
#     "finance_manager": "...",
#     "authorized_signatory": "..."
#   }},
#   "payment_details": {{
#     "total": 0,
#     "in_words": "...",
#     "discount": 0,
#     "taxable_amount": 0,
#     "vat": 0,
#     "net_amount": 0
#   }},
#   "line_items": [
#     {{
#       "hs_code": "...",
#       "particulars": "...",
#       "qty": "...",
#       "rate": "...",
#       "amount": "..."
#     }}
#   ]
# }}

# Text:
# \"\"\"
# {plain_text}
# \"\"\"

# Important: Return ONLY the JSON object. No explanations, no headings, no extra text.
# """

#     try:
#         response = client.chat.complete(
#             model="mistral-small-latest",
#             messages=[{"role": "user", "content": extraction_prompt}]
#         )

#         raw = response.choices[0].message.content
#         cleaned = re.sub(r"^```(?:json)?\s*|```$", "", raw.strip(), flags=re.MULTILINE)
#         return cleaned
    
#     except Exception as e:
#         return f"Error during structured extraction: {str(e)}"

# st.title("Invoice Extractor")

# uploaded_file = st.file_uploader("Choose a PDF...", type=["pdf"])

# if uploaded_file is not None:
#     file_type = uploaded_file.type
#     if file_type == "application/pdf":
#         with st.spinner("Reading PDF"):
#             plain_text = extract_text_from_pdf_plumber(uploaded_file)
#             st.subheader("Extracted Text from PDF:")
#             st.text_area("Text Content", plain_text, height=1000)

#             if st.button("Extract Structured Data"):
#                 structured_json = extract_structured_text(plain_text)
#                 st.subheader("Structured Data:")
#                 st.json(structured_json)




#using pdf plumber and scanned pdf handled
# import streamlit as st
# import base64
# import requests
# import os
# from mistralai import Mistral
# from dotenv import load_dotenv
# from PIL import Image
# import io
# import pdfplumber
# import fitz  
# import re


# load_dotenv()
# api_key = os.getenv("MISTRAL_API_KEY")


# client = Mistral(api_key=api_key)

# def extract_text_from_pdf_plumber(file):
#     with pdfplumber.open(file) as pdf:
#         text = pdf.pages[0].extract_text()
#     return text

# def is_scanned_pdf(file):
#     """Detect scanned PDFs by checking text length and image coverage."""
#     try:
#         file.seek(0)  # Ensure file pointer is at start
#         with pdfplumber.open(file) as pdf:
#             first_page = pdf.pages[0]
#             text = first_page.extract_text()
            
#             if not text or len(text.strip()) < 50:
#                 return True
#     except Exception:
#         return True 

# def convert_pdf_page_to_image(file):
#     """Convert first page of PDF to a PIL Image using PyMuPDF (fitz)."""
#     file.seek(0)
#     pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
#     page = pdf_doc.load_page(0)
#     pix = page.get_pixmap(dpi=300)
#     img = Image.open(io.BytesIO(pix.tobytes("png")))
#     return img

# def encode_image(image):
#     img_byte_array = io.BytesIO()
#     image.save(img_byte_array, format="PNG") 
#     base64_encoded = base64.b64encode(img_byte_array.getvalue()).decode("utf-8")
#     return base64_encoded

# def extract_text_from_image(image):
#     base64_image = encode_image(image)
    
#     messages = [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "Below is the image of one page of a document, as well as some raw textual content that was previously extracted for it. Just return the plain text representation of this document as if you were reading it naturally. Do not hallucinate."
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": f"data:image/png;base64,{base64_image}"
#                 }
#             ]
#         }
#     ]
    
#     try:
#         response = client.chat.complete(
#             model="mistral-small-latest",
#             messages=messages
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         return f"Error: {str(e)}"

# def extract_structured_text(plain_text):
#     extraction_prompt = f"""
# You are an expert document parser specializing in commercial documents like invoices, bills, and insurance papers.

# Extract the following structured data from the document text:
# - vendor_details: name, address, phone, email, website, PAN
# - customer_details: name, address, contact, PAN (usually below vendor_details)
# - invoice_details: bill_number, bill_date, transaction_date, mode_of_payment, finance_manager, authorized_signatory
# - payment_details: total, in_words, discount, taxable_amount, vat, net_amount
# - line_items (list): hs_code, description, qty, rate, amount

# Rules:
# 1. Extract only the fields listed; do not guess or add extra fields.
# 2. If a field is missing, set its value as null.
# 3. Use context ('Vendor', 'Supplier', 'Bill To', 'Customer', etc.) to distinguish parties. If unclear, the first business is Vendor, the second is Customer.
# 4. Each line_item must include hs_code and description; qty, rate, and amount are optional.
# 5. Always return the result strictly in the following JSON structure.
# 6. PAN numbers are typically boxed or near labels like 'PAN No.', and follow a 9-digit (Nepal) format.

# Return the structured data using this exact JSON format:

# {{
#   "vendor_details": {{
#     "name": "...",
#     "address": "...", 
#     "phone": "...", 
#     "email": "...",
#     "website": "...",
#     "pan": "..."
#   }},
#   "customer_details": {{
#     "name": "...",
#     "address": "...",
#     "contact": "...",
#     "pan": "..."
#   }},
#   "invoice_details": {{
#     "bill_number": "...",
#     "bill_date": "...",
#     "transaction_date": "...",
#     "mode_of_payment": "...",
#     "finance_manager": "...",
#     "authorized_signatory": "..."
#   }},
#   "payment_details": {{
#     "total": 0,
#     "in_words": "...",
#     "discount": 0,
#     "taxable_amount": 0,
#     "vat": 0,
#     "net_amount": 0
#   }},
#   "line_items": [
#     {{
#       "hs_code": "...",
#       "particulars": "...",
#       "qty": "...",
#       "rate": "...",
#       "amount": "..."
#     }}
#   ]
# }}

# Text:
# \"\"\"
# {plain_text}
# \"\"\"

# Important: Return ONLY the JSON object. No explanations, no headings, no extra text.
# """
#     try:
#         response = client.chat.complete(
#             model="mistral-small-latest",
#             messages=[{"role": "user", "content": extraction_prompt}]
#         )

#         raw = response.choices[0].message.content
#         cleaned = re.sub(r"^```(?:json)?\s*|```$", "", raw.strip(), flags=re.MULTILINE)
#         return cleaned
#     except Exception as e:
#         return f"Error during structured extraction: {str(e)}"


# st.title("PDF Invoice Extractor")

# uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

# if uploaded_file is not None:
#     with st.spinner("Analyzing PDF..."):
#         if is_scanned_pdf(uploaded_file):
#             st.info("Scanned PDF detected. Using OCR for extraction.")
#             image = convert_pdf_page_to_image(uploaded_file)
#             plain_text = extract_text_from_image(image)
#         else:
#             st.info("Digital PDF detected. Using text extraction.")
#             uploaded_file.seek(0) 

#             plain_text = extract_text_from_pdf_plumber(uploaded_file)

#     st.subheader("Extracted Raw Text")
#     st.text_area("Raw Content", plain_text, height=800)

#     if st.button("Extract Structured Data"):
#         structured_data = extract_structured_text(plain_text)
#         st.subheader("Structured Data")
#         st.json(structured_data)
