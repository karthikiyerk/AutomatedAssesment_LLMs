from crewai import Task
from textwrap import dedent


class DocumentTasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"

    def plan_document(self, agent, ques, ip_ans, g_scheme, des_ans):
        return Task(
            description=dedent(
                f"""
            **Task**: Develop a 2 part document containing Grades and Feedback
            **Description**: Create a document that has student answer, grades based on grading scheme and feedback based on Desired Answer.
            For the given Question, compare the student answer with the Desired Answer and then follow the Grading Scheme as reference for Grading. Then based on this create a short Feedback.

            **Parameters**: 
            - Question: {ques}
            - Input Answer: {ip_ans}
            - Grading Scheme: {g_scheme}
            - Desired Answer: {des_ans}

        """
            ),
            agent=agent,
        )

    def create_grade(self, agent, ip_ans, des_ans, g_scheme):
        return Task(
            description=dedent(
                f"""
                    **Task**:  Identify the Best Grade for the student answer
                    **Description**: Compare the Student Answer and the Desired Answer. Then according to the Grading Scheme come up with a Grade for the student.


                    **Parameters**: 
                    - Input Answer: {ip_ans}
                    - Desired Answer: {des_ans}
                    - Grading Scheme: {g_scheme}

                    **Note**: {self.__tip_section()}
        """
            ),
            agent=agent,
        )

    def create_feedback(self, agent, ip_ans, des_ans):
        return Task(
            description=dedent(
                f"""
                    **Task**:  Produce a proper feedback based on the marks and the desired answer
                    **Description**: Compile an in-depth guide feedback for the student answer and marks based on 
                        the student's Input Answer and comparing it with the Desired Answer. 
                        This guide SHOULD provide an overview of what was missing from the answer on comparison with Desired Answer,
                        and include comments on the student answer and the corrections if required.

                    **Parameters**: 
                    - Input Answer: {ip_ans}
                    - Desired Answer: {des_ans}

                    **Note**: {self.__tip_section()}
        """
            ),
            agent=agent,
        )