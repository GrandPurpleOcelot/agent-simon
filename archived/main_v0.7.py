import streamlit as st
from docx import Document
from io import BytesIO
import openai
import json

# Connect to OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]

def read_docx(file):
    """Read and parse a docx file, returning the text content."""
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def parse_markdown_table(md_table):
    """Generate a response from OpenAI in JSON format."""
    instruction_message = "Parse the table in markdown table to Json format"
    try:
        openai_response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": instruction_message},
                {"role": "user", "content": md_table}
            ],
            temperature=0.5,
            max_tokens=2000,
        )

        data_dicts =  json.loads(openai_response.choices[0].message.content)
        return data_dicts
        
    except Exception as e:
        st.error(f"Error in generating JSON response from OpenAI: {e}")
        return None

def generate_plan(transcript_text):
    """Generate a requirement plan using OpenAI."""
    try:
        openai_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Generate a high-level software requirements document based on the transcript text. The plan describes the overview of the system functions or business processes. Besure to include Ojective and Requirements for each component. Keep the plan concise and relevant to software functions."},
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
    instruction_message = f"""Generate a table with three columns: item #, object, description, based on the requirement plan. {nl_instruction}"""
    openai_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instruction_message},
            {"role": "user", "content": plan}
        ],
        temperature=0.5,
        max_tokens=2000
    )
    descriptions = openai_response.choices[0].message.content

    return descriptions

def generate_workflow(plan, actor_objects):
    """Generate a user workflow based on the requirement plan and actor objects table."""
    instruction_message = """Generate a detailed user workflow combining the requirements and actor interactions.\n
    This section shows the flow of tasks or steps taken by the main actor(s) - the user of the software system,  to complete a business process.\n
    The actor’s actions are shown in each business process stage of the system along with the conditions (if/else) under which it can move to the next stage or revert to the previous.\n
    """
    openai_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instruction_message},
            {"role": "user", "content": f"Requirements Plan:\n{plan}\nActor Objects:\n{actor_objects}"}
        ],
        temperature=0.5,
        max_tokens=2000
    )
    workflow = openai_response.choices[0].message.content
    return workflow

def generate_state_transitions(plan, data_objects):
    """Generate state transition steps based on the plan and Data Objects Table."""
    instruction_message = "Generate state transition steps for the software based on the requirements plan and data objects."
    openai_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instruction_message},
            {"role": "user", "content": f"Requirements Plan:\n{plan}\nData Objects:\n{data_objects}"}
        ],
        temperature=0.5,
        max_tokens=2000
    )
    state_transitions = openai_response.choices[0].message.content
    return state_transitions

def generate_use_case_table(plan, actor_objects):
    """Generate a use case description table based on the plan and Actor Objects Table."""
    instruction_message = "Generate a detailed use case table including columns: UC_ID, UC_Name (e.g User Login, View Error details), and Description to describe each actor's interactions with the system based on the requirements plan."
    openai_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instruction_message},
            {"role": "user", "content": f"Requirements Plan:\n{plan}\nActor Objects:\n{actor_objects}"}
        ],
        temperature=0.5,
        max_tokens=2000
    )
    use_case_table = openai_response.choices[0].message.content
    return use_case_table

def generate_permission_matrix(actor_objects, use_case_table):
    """Generate a permission matrix table based on Actor Objects Table and Use Case Table."""
    instruction_message = """Generate a permission matrix showing which actors have access to which use cases.\n
    Columns are Actor and row are UC name\n
    Cell values:
    “O” means that user has permission on corresponding function. For more information about what the actor can do on that function, please refer to corresponding use case.\n
    “O*” means that user has permission on corresponding function on the item they created. For more information about what the actor can do on that function, please refer to corresponding use case.\n
    “X” means that user does not have permission on corresponding function.
    """
    openai_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instruction_message},
            {"role": "user", "content": f"Actor Objects:\n{actor_objects}\nUse Case Table:\n{use_case_table}"}
        ],
        temperature=0.5,
        max_tokens=2000
    )
    permission_matrix = openai_response.choices[0].message.content
    return permission_matrix

def generate_use_case_specs(use_case):
    """Generate detailed specifications for a use case."""
    try:
        openai_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """Generate a concise specifications table including the follow rows:\n 
                 Objective, Actor, Trigger, Pre-condition, Post-condition, Acceptan Criteria for the following use case."""},
                {"role": "user", "content": f"Use Case Name: {use_case['UC_Name']}\nDescription: {use_case['Description']}"}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        return openai_response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating specifications: {e}")
        return "Error generating specifications."

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
            data_objects = generate_table(st.session_state['plan'], "List all data objects within the software system. For example, the data object can be Devices, Customer Profile, Product, Account, Case, Step-ABC.")
            st.session_state['data_objects'] = data_objects

        if st.button("Generate Actor Objects Table"):
            actor_objects = generate_table(st.session_state['plan'], "List all actors that directly interact with the software. For example actors can be Sensor, Worker, Customer, QC Specialist, Supervisor, etc.")
            st.session_state['actor_objects'] = actor_objects

        if st.button("Generate External System Objects Table"):
            external_systems = generate_table(st.session_state['plan'], "List all external systems or services that the software will interact with. For example external system can be CRM, Active Directory, Sales Management System etc.")
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

    if 'actor_objects' in st.session_state and 'plan' in st.session_state:
        if st.button("Generate Workflow"):
            workflow = generate_workflow(st.session_state['plan'], st.session_state['actor_objects'])
            st.session_state['workflow'] = workflow

    if 'workflow' in st.session_state and 'data_objects' in st.session_state:
        if st.button("Generate State Transition"):
            state_transitions = generate_state_transitions(st.session_state['plan'], st.session_state['data_objects'])
            st.session_state['state_transitions'] = state_transitions

    if 'actor_objects' in st.session_state and 'plan' in st.session_state:
        if st.button("Generate Use Case Table"):
            use_case_table = generate_use_case_table(st.session_state['plan'], st.session_state['actor_objects'])
            st.session_state['use_case_table'] = use_case_table
            # Parse and store in session state
            st.session_state['use_cases'] = parse_markdown_table(use_case_table)

    if 'use_cases' in st.session_state:
        if st.button("Generate Use Case Specs"):
            # Initialize an empty list to store all use case specifications
            use_case_specs = []
            
            # Create a placeholder for real-time updates
            real_time_placeholder = st.empty()
            
            # Create a placeholder for accumulated results
            accumulated_results_placeholder = st.empty()
            accumulated_results = ""  # Start with an empty string to accumulate results
            
            # Loop through each use case and generate specifications
            for index, use_case in enumerate(st.session_state['use_cases']['use_cases']):
                # Generate specifications for the current use case
                description = generate_use_case_specs(use_case)
                
                # Append the new specification to the list
                use_case_specs.append(description)
                
                # Display the specification being processed in real-time
                real_time_placeholder.markdown(f"Processing use case {index + 1}/{len(st.session_state['use_cases']['use_cases'])}...")
                
                # Update the accumulated results with the new specification
                accumulated_results += f"**Use Case {index + 1}:**\n{description}\n\n"
                accumulated_results_placeholder.markdown(accumulated_results)
            
            # Clear the real-time placeholder once all specs are processed
            real_time_placeholder.empty()
            
            # Update session state with all generated use case specifications
            st.session_state['use_case_specs'] = use_case_specs
            
            # Display a completion message or any additional information
            st.success("All use case specifications have been generated successfully!")
    # Display the generated use case specifications
    if 'use_case_specs' in st.session_state:
        st.write("### Generated Use Case Specifications:")
        for spec in st.session_state['use_case_specs']:
            st.text(spec)

    if 'use_case_table' in st.session_state and 'actor_objects' in st.session_state:
        if st.button("Generate Permission Matrix"):
            permission_matrix = generate_permission_matrix(st.session_state['actor_objects'], st.session_state['use_case_table'])
            st.session_state['permission_matrix'] = permission_matrix

    if 'workflow' in st.session_state:
        st.write("### Generated User Workflow:")
        st.markdown(st.session_state['workflow'])

    if 'state_transitions' in st.session_state:
        st.write("### Generated State Transitions:")
        st.markdown(st.session_state['state_transitions'])

    if 'use_case_table' in st.session_state:
        st.write("### Generated Use Case Table:")
        st.markdown(st.session_state['use_case_table'])

    if 'permission_matrix' in st.session_state:
        st.write("### Generated Permission Matrix:")
        st.markdown(st.session_state['permission_matrix'])

if __name__ == "__main__":
    main()