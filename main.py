import streamlit as st
from docx import Document
from io import BytesIO
import os
import base64
import openai
import json
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import copy
from copy import deepcopy

def read_docx(file):
    """Read and parse a docx file, returning the text content."""
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def main():
    st.title('Docx Reader')
    st.subheader('Upload a .docx file to display its content')

    uploaded_file = st.file_uploader("Choose a file", type='docx')
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        text = read_docx(BytesIO(bytes_data))
        st.write("### Document Content:")
        st.text_area("Content", value=text, height=300)

if __name__ == "__main__":
    main()