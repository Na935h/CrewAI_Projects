from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class FinancialResearcher():
    """FinancialResearcher crew"""

    # agents: List[BaseAgent]
    # tasks: List[Task]
    agents_config= 'config/agents.yaml'
    tasks_config= 'config/tasks.yaml'

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()]
            
        )

    @agent
    def analyst(self) -> Task:
        return Agent(
            config=self.agents_config['analyst'],
            verbose=True
            ) # type: ignore[index]
    
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task']) # type: ignore[index]
    
    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'])
             # type: ignore[index]
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )