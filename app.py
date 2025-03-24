import streamlit as st
import base64
import requests
import os
from mistralai import Mistral
from dotenv import load_dotenv
from PIL import Image
import io

# Load API key from .env file
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# Initialize Mistral AI client
client = Mistral(api_key=api_key)

def encode_image(image):
    """Encode an uploaded image to base64."""
    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format="PNG")  # Convert image to bytes
    base64_encoded = base64.b64encode(img_byte_array.getvalue()).decode("utf-8")
    return base64_encoded

def extract_text_from_image(image):
    """Send the image to Mistral AI OCR and extract text."""
    base64_image = encode_image(image)
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Below is the image of one page of a document, as well as some raw textual content that was previously extracted for it. Just return the plain text representation of this document as if you were reading it naturally. Do not hallucinate."
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{base64_image}"
                }
            ]
        }
    ]
    
    model = "mistral-small-latest"
    
    # Send request to Mistral API
    try:
        chat_response = client.chat.complete(model=model, messages=messages)
        return chat_response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("Extracting Invoice Text")
st.write("Upload an image to extract text.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Extract Text"):
        with st.spinner("Extracting text..."):
            extracted_text = extract_text_from_image(image)
        
        st.subheader("Extracted Text:")
        st.text_area("OCR Output", extracted_text, height=500)

