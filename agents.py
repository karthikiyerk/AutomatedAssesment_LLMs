import os
from crewai import Agent
from textwrap import dedent
from langchain_openai import ChatOpenAI
#from langchain_grog import ChatGroq
from crewai_tools import PDFSearchTool

from tools.search_tool import SearchTools
from tools.calculator_tools import CalculatorTools


# TO_DO
# _______
#   1. LLM Setup
#   2. Tool Define+Connect
#

#The Agent Overview
# """
    # Agents:
        # Goal:
        # - Create a 3-part document with grade and feedback for college assignments; 
        #   1st Part-Student Answer(I/P), 2nd Part-Grade and 3rd Part-Feedback
        
        # Captain/Manager/Boss:
        # - Expert Tutor Agent

        # Employees/Experts to hire:
        # - Grading Expert 
        # - Feedback Expert
        #   : In future in necessary can be split to Descriptive and Programming agents separately


class DocumentAgents:
    def __init__(self):
        self.OpenAIGPT35 = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7) # type: ignore
        self.OpenAIGPT4omini = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)  # type: ignore
        self.OpenAIGPT4 = ChatOpenAI(model_name="gpt-4", temperature=0.7) # type: ignore # 2Euros Per GTP4 for a single RUN!
        #self.LLama3 = ChatGroq(api_key=os.getenv("GROQ_API_KEY") model_name="llama3.1:8b")
        self.LLama3 = ChatOpenAI(model="crewai-llama3.18b", base_url="http://localhost:11434/v1", temperature=0.8)
        self.DeepSeek = ChatOpenAI(model="crewai-DeepSeekr1", base_url="http://localhost:11434/v1", temperature=0.8)
        
    def expert_tutor_agent(self):
        return Agent(
            role="Expert Tutor Agent",
            backstory=dedent(
                f"""An expert tutor who summarizes grading and feedback effectively. 
            You ensure the output remains structured and concise."""),
            goal=dedent(f"""
                        Combine the outputs from the **Grading Expert** and **Feedback Expert**  
            into a final structured summary.  
            
            **Final Response Format:**  
            ```
            Grade: [ X / Y ]
            Feedback: [ Short, focused feedback ]
            ```
            - Keep everything under **300 words**.
            - Ensure readability and brevity.
                        """),
            #tools=[
            #    SearchTools.search_internet,
            #    CalculatorTools.calculate
            #],
            verbose=True,
            llm=self.DeepSeek,
        )

    def grading_expert(self):
        return Agent(
            role="Grading Expert",
            backstory=dedent(
                f"""A precise grader with decades of experience. 
                    """),
            goal=dedent(
                f"""You first compare the Student Answer and the Desired Answer, Then strictly 
                according to grading scheme assign a grade.  
            
            **Response Format:**  
            ```
            Grade: [ X / Y ]
            ```
            - No explanations, just the grade.
            - Keep it minimal and accurate.
            """),
            tools=[CalculatorTools.calculate],
            verbose=True,
            llm=self.DeepSeek,
        )

    def feedback_expert(self):
        return Agent(
            role="Feedback Expert",
            backstory=dedent(f"""An experienced tutor specializing in precise, constructive feedback.
            You provide focused feedback on student answers."""),
            goal=dedent(
                f"""Compare the student's answer with the correct answer and give short feedback.  
            
            **Response Format:**  
            ```
            Feedback: [ Your response is clear, but lacks examples. Consider adding one. ]
            ```
            - Keep it **under 2 sentences**.
            - No explanations beyond necessary corrections."""),
            #tools=[SearchTools.search_internet],
            verbose=True,
            llm=self.DeepSeek,
        )

