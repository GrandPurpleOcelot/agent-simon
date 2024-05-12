import streamlit as st
from docx import Document
from io import BytesIO
import openai

# Connect to OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]

def read_docx(file):
    """Read and parse a docx file, returning the text content."""
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def generate_plan(transcript_text):
    """Generate a requirement plan using OpenAI."""
    try:
        openai_response = openai.chat.completions.create(
             model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "Generate a high-level software requirements based on the transcript text. Keep the plan concise and relevant."},
                {"role": "user", "content": "Below is the transcript from the meeting:\n {}".format(transcript_text)}
            ],
            temperature=0.5,
            max_tokens=2500
        )

        generated_text = openai_response.choices[0].message.content

        return generated_text
    
    except Exception as e:
        st.error(f"An error occurred with the OpenAI API: {e}")
        return None

def main():
    st.title('Agent Simon - Minutes to Requirements')

    uploaded_file = st.file_uploader("Upload a Teams meeting transcript .docx file", type='docx')
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        text = read_docx(BytesIO(bytes_data))
        st.write("### Document Content:")
        st.text_area("Content", value=text, height=300)

        if st.button("Generate Requirement Plan"):
            plan = generate_plan(text)
            if plan:
                st.write("### Generated Requirement Plan:")
                st.markdown(plan)

if __name__ == "__main__":
    main()