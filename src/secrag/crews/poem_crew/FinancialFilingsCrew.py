from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai import LLM
import os


# 1. Import your custom tool and the Gemini LLM

# from langchain_google_genai import ChatGoogleGenerativeAI

@CrewBase
class FinancialFilingsCrew():
    """FinancialFilingsCrew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # 2. Initialize the Gemini model with a valid model name
    llm = LLM(model="gemini/gemini-2.0-flash",
                                 verbose=True,
                                 temperature=0.5,
                                 api_key=os.environ.get("GEMINI_API_KEY")
                                 )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'],
            
            # 3. Assign the LLM to the agent
            llm=self.llm
        )

    @agent
    def report_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['report_analyst'],
            verbose=True,
            # 3. Assign the LLM to the agent
            llm=self.llm
        )

    @task
    def analyze_filings_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_filings_task'],
            agent=self.financial_researcher()
        )

    @task
    def summarize_filings_task(self) -> Task:
        return Task(
            config=self.tasks_config['summarize_filings_task'],
            agent=self.report_analyst(),
            output_file='sec_filings_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the FinancialFilingsCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
