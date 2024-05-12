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

def generate_table(plan, nl_instruction):
    """Generate tables based on the requirement plan."""
    instruction_message = f"Generate a table with three column: item, object, description, based on the requirement plan. {nl_instruction}"
    openai_response = openai.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": instruction_message},
            {"role": "user", "content": plan}
        ],
        temperature=0.5,
        max_tokens=500
    )
    descriptions = openai_response.choices[0].message.content
    return descriptions

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
                st.session_state['plan'] = plan  # Save plan to session state

    if 'plan' in st.session_state:
        st.write("### Generated Requirement Plan:")
        st.markdown(st.session_state['plan'])

        if st.button("Generate Data Objects Table"):
            data_objects = generate_table(st.session_state['plan'], "List all data objects within the software system.")
            st.session_state['data_objects'] = data_objects

        if st.button("Generate Actor Objects Table"):
            actor_objects = generate_table(st.session_state['plan'], "List all actors that interact with the software.")
            st.session_state['actor_objects'] = actor_objects

        if st.button("Generate External System Objects Table"):
            external_systems = generate_table(st.session_state['plan'], "List all external systems or services that the software might interact with.")
            st.session_state['external_systems'] = external_systems

        if 'data_objects' in st.session_state:
            st.write("### Data Objects Table:")
            st.markdown(st.session_state['data_objects'])

        if 'actor_objects' in st.session_state:
            st.write("### Actor Objects Table:")
            st.markdown(st.session_state['actor_objects'])

        if 'external_systems' in st.session_state:
            st.write("### External Systems Table:")
            st.markdown(st.session_state['external_systems'])

if __name__ == "__main__":
    main()