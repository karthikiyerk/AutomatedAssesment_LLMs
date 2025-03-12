## Abstract
##---------

This repository contains the code and documentation for a thesis project focused on the development of an Agentic System 
for grading assessments and providing feedback using advanced Generative AI models. The system integrates OpenAI’s GPT-4o, 
LangChain, and CrewAI to automate the grading and feedback process. The architecture consists of a ManagerAgent that 
distributes tasks to specialized agents: one for grading and one for providing feedback. The solution is built on a 
Streamlit frontend, allowing users to upload assessment files, which are then processed and stored in Neo4j for further analysis.

## Installation and Running Guide
##-------------------------------

## Prerequisites
1. Python Installation
   - Ensure Python version >= 3.10 and < 3.12 is installed.
   - [Download Python](https://www.python.org/downloads/) if not already installed.

2. Poetry Installation
   - Install Poetry for Python package management:
     ```bash
     curl -sSL https://install.python-poetry.org | python3 -
     ```
   - Verify installation:
     ```bash
     poetry --version
     ```

3. Neo4j Database Setup
   - Install Neo4j Desktop or use Neo4j Aura for cloud-based services.
   - Start Neo4j and create a database.
   - Set and note down the URI, Username, and Password.

4. Environment Variables
   - Create a `.env` file in the root directory and add:
     ```env
     NEO4J_URI=bolt://localhost:7687
     NEO4J_USERNAME=neo4j
     NEO4J_PASSWORD=your_password
     ```

## Installation Steps
#--------------------

1. Clone the Repository
   ```bash
   git clone <repository-url>
   cd RedSquirrel_0.0
   ```

2. Install Dependencies
   - Install project dependencies using Poetry:
     ```bash
     poetry install
     ```

3. Activate the Virtual Environment
   ```bash
   poetry shell
   ```
Note: The project dependencies are saved in the poetry file and will create a environment with the required dependencies.

## Running the Project
##--------------------
1. Start the Streamlit Application
   ```bash
   streamlit run 'master.py'
   ```

2. Neo4j Connection Check
   - The application will attempt to connect to the Neo4j database upon startup.
   - Verify the connection status in the Streamlit sidebar.

3. Uploading Files
   - Follow the UI steps to upload the master file and student input files for processing.

4. View and Save Results
   - Review the evaluated results and assign ratings through the UI.
   - Save the ratings, which will be persisted into the Neo4j database.


## Common Troubleshooting
## -----------------------
- Neo4j Connection Issues
   - Verify the URI, username, and password in the `.env` file.
   - Ensure the Neo4j service is running and accessible.

- Poetry Installation Issues
   - Ensure Python version compatibility with Poetry.
   - Reinstall Poetry if issues persist.

- Dependency Errors
   - Run the following command to resolve:
     ```bash
     poetry lock --no-update
     poetry install
     ```
    PS: If you cannot install dependencies properly, please install all dependencies using anaconda or other methods.

