from crewai import Crew
from textwrap import dedent
from agents import DocumentAgents
from tasks import DocumentTasks
import streamlit as st
import os
from neo4j import GraphDatabase
from langchain_community.graphs.neo4j_graph import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from typing import List, Sequence, cast


from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Function to save uploaded files for later processing
def save_file(uploaded_file, file_path):
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Function to check Neo4j connection status
def check_db_connection(uri, user, password):
    try:
        # Attempt to create a Neo4j driver instance
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            session.run("RETURN 1")  # Simple query to verify connection
        driver.close()
        return True
    except Exception as e:
        print(f"Connection error: {e}")
        return False


class DocCrew:
    def __init__(self, ques, ip_ans, g_scheme, des_ans):
        #Simple Constructor to init vars
        self.ques = ques
        self.ip_ans = ip_ans
        self.g_scheme = g_scheme
        self.des_ans = des_ans

    def run(self):
        agents = DocumentAgents()
        tasks = DocumentTasks()

        # Define your custom agents and tasks here
        expert_tutor_agent = agents.expert_tutor_agent()
        grading_expert = agents.grading_expert()
        feedback_expert = agents.feedback_expert()

        # Custom tasks include agent name and variables as input
        plan_document = tasks.plan_document(
            expert_tutor_agent,
            self.ques,
            self.ip_ans,
            self.g_scheme,
            self.des_ans
        )

        create_grade = tasks.create_grade(
            grading_expert,
            self.ip_ans,
            self.des_ans,
            self.g_scheme
        )

        create_feedback = tasks.create_feedback(
            feedback_expert,
            self.ip_ans,
            self.des_ans
        )

        # Define your custom crew here
        crew = Crew(
            agents=[expert_tutor_agent,
                    grading_expert,
                    feedback_expert
                    ],
            tasks=[
                plan_document
            ],
            verbose=True,
        )

        result = crew.kickoff()
        return result


# Function to read the contents of the file and extract sections
def extract_sections_master(file_path):
    sections = {}
    with open(file_path, 'r') as file:
        data = file.read()
        # Split based on keywords to parse the content into sections
        sections['Subject Name'] = data.split("Subject Name : ")[1].split("\n")[0]
        sections['ID'] = data.split("ID: ")[1].split("\n")[0]
        sections['Question'] = data.split("Question: ")[1].split("Desired Answer:")[0].strip()
        sections['Desired Answer'] = data.split("Desired Answer: ")[1].split("Grading Scheme:")[0].strip()
        sections['Grading Scheme'] = data.split("Grading Scheme: ")[1].strip()
    
    return sections

def extract_sections_student(file_path):
    sections = {}
    with open(file_path, 'r') as file:
        data = file.read()
        # Split based on keywords to parse the content into sections
        sections['Student Name'] = data.split("Student Name: ")[1].split("\n")[0]
        sections['Subject'] = data.split("Subject: ")[1].split("\n")[0]
        sections['ID'] = data.split("ID: ")[1].split("\n")[0]
        sections['Student Answer'] = data.split("Answer: ")[1].strip()
    return sections

# Function to create Cypher query for inserting nodes into Neo4j
def create_Master_query(sections):
    cyp_query = f"""
    CREATE (s:Subject {{name: '{sections['Subject Name']}', id: '{sections['ID']}'}})
    CREATE (q:Question {{text: '{sections['Question']}'}})
    CREATE (a:Answer {{text: '{sections['Desired Answer']}'}})
    CREATE (g:GradingScheme {{scheme: '{sections['Grading Scheme']}'}})
    CREATE (s)-[:HAS_QUESTION]->(q)
    CREATE (q)-[:HAS_ANSWER]->(a)
    CREATE (q)-[:HAS_GRADING_SCHEME]->(g)
    """
    return cyp_query

def create_student_query(student_sections, rating):
    stud_cyp_query = f"""
    CREATE (student:Student {{name: '{student_sections['Student Name']}', id: '{student_sections['ID']}', rating: '{rating}'}})
    CREATE (sub:Subject {{name: '{student_sections['Subject']}'}})
    CREATE (ans:StudentAnswer {{text: '{student_sections['Student Answer']}'}})
    
    CREATE (student)-[:ENROLLED_IN]->(sub)
    CREATE (student)-[:SUBMITTED]->(ans)
    """
    return stud_cyp_query

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def process_input_file(file_path, master_question, master_grading_scheme, master_desired_answer):
    # Extract sections from student answer file
    student_sections = extract_sections_student(file_path)
    student_answer = student_sections.get('Student Answer')

    if student_answer:
        # Execute AI Crew to generate result
        document_crew = DocCrew(master_question, student_answer, master_grading_scheme, master_desired_answer)
        generated_result = document_crew.run()
        return generated_result, student_sections
    else:
        return "No student answer found in the file."

# This is the main function that you will use to run your custom crew.
if __name__ == "__main__":
        
    # Streamlit UI
    st.title("Thesis - Automated Assessment System Using Language Models")    
    
    #NEO4J Initialization
    #-------------------
    print("Intitalize Graph DB for Neo4j")
        
    if check_db_connection(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD):
        st.sidebar.markdown(f"🟢 **Connected** to Neo4j\nURI: {NEO4J_URI}\nUser: {NEO4J_USERNAME}")
    else:
        st.sidebar.markdown(f"🔴 **Disconnected**\nURI: {NEO4J_USERNAME}\nUser: {NEO4J_USERNAME}")
    
    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)
    
    
    # Section 1: Upload Master File
    st.header("Step 1: Upload Master File")
    master_file = st.file_uploader("Please upload the Master document that contains the Subject, ID, Question, Desired Answer and Grading Scheme ", type=["txt"], key="master_file")
    if master_file is not None:
        master_file_path = save_file(master_file, "master_file.txt")
        st.success("Master file uploaded successfully.")

    #For uploading to DB
    master_sections = extract_sections_master(master_file_path)
    
    #Extract Desired Answer and Grading Scheme
    master_desired_answer = master_sections['Desired Answer']
    master_grading_scheme = master_sections['Grading Scheme']
    master_question = master_sections['Question']

    #Upload Master Section to DB with Master Query!
    c_query = create_Master_query(master_sections)
    graph.query(c_query)

    # Section 2: Upload Multiple Input Files
    st.header("Step 2: Upload Student Input Files")
    input_files = st.file_uploader("Upload Input Files of students containing Student Name, Subject, ID, and Student Answer", type=["txt"], accept_multiple_files=True, key="input_files")
    input_file_paths = []
    results = []
    student_sections_list = []

    if "ratings" not in st.session_state:
        st.session_state.ratings = {}

    if input_files:
        for uploaded_file in input_files:
            file_path = save_file(uploaded_file, uploaded_file.name)
            input_file_paths.append(file_path)            
        st.success(f"{len(input_files)} input files uploaded successfully.")

    # Button to submit and evaluate
    if st.button("Submit and Evaluate"):
        st.session_state.show_results = True
        for file_path in input_file_paths:
            result, student_sections = process_input_file(file_path, master_question, master_grading_scheme, master_desired_answer)
            results.append({"file_name": file_path, "output_text": result})
            student_sections_list.append(student_sections)
        
    if st.session_state.get("show_results", False):
        st.header("Step 3: Results")
    for file, sections in zip(results, student_sections_list):
        with st.container():
            st.write(f"### File: {file['file_name']}")

            rating_options = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
            selected_rating = st.radio(
                f"Rate for {file['file_name']}:",
                options=rating_options,
                index=st.session_state.ratings[file["file_name"]] - 1,
                key=f"rating_{file['file_name']}",
                horizontal=True
            )

            st.session_state.ratings[file["file_name"]] = rating_options.index(selected_rating) + 1

            st.markdown(
                f"<div style='padding: 5px; background-color: #f0f0f0; border-radius: 5px; "
                f"display: inline-block; font-weight: bold;'>Selected: {selected_rating}</div>",
                unsafe_allow_html=True
            )

            with st.expander(f"Show Details for {file['file_name']}"):
                st.text_area("", file["output_text"], height=200, key=f"details_{file['file_name']}")

            query = create_student_query(sections, st.session_state.ratings[file["file_name"]])
            graph.query(query)  # Execute the student query

            st.divider()

    if st.button("Save Ratings"):
        st.write("### Saved Ratings:")
        for file, rating in st.session_state.ratings.items():
            st.write(f"📁 {file}: {'⭐' * rating}")

