from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from langchain_community.tools import DuckDuckGoSearchRun

@CrewBase
class HTMLRenderCrew:
    """A crew that takes markdown content and converts it into a styled HTML page."""
    
    # The agents_config and tasks_config attributes point to the YAML files
    # that define the roles, goals, and descriptions for our agents and tasks.
    # agents_config = 'src/secfilingsparser/crews/htmlrendercrew/config/agents.yaml'
    # tasks_config = 'src/secfilingsparser/crews/htmlrendercrew/config/tasks.yaml'

    @agent
    def markdown_converter(self) -> Agent:
        """Agent responsible for converting markdown to raw HTML."""
        return Agent(
            config=self.agents_config['markdown_converter'],
            tools=[DuckDuckGoSearchRun()], # Tools can be added here
            verbose=True,
            allow_delegation=False
        )

    @agent
    def html_stylist(self) -> Agent:
        """Agent responsible for styling the raw HTML."""
        return Agent(
            config=self.agents_config['html_stylist'],
            verbose=True,
            allow_delegation=False
        )

    @task
    def convert_task(self) -> Task:
        """Task to convert markdown to HTML."""
        return Task(
            config=self.tasks_config['convert_to_html'],
            agent=self.markdown_converter()
        )

    @task
    def style_task(self) -> Task:
        """Task to style the HTML page."""
        return Task(
            config=self.tasks_config['style_html_page'],
            agent=self.html_stylist(),
            context=[self.convert_task()],
            output_file='output.html'
        )

    @crew
    def crew(self) -> Crew:
        """Creates and returns the HTMLRenderCrew."""
        return Crew(
            agents=self.agents,  # The agents are automatically populated by the @agent decorator
            tasks=self.tasks,    # The tasks are automatically populated by the @task decorator
            process=Process.sequential,
            verbose=True
        )

# This block allows the crew to be run directly from the command line for testing.



