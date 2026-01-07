# # from crewai import Agent, Task, Crew, Process
# # from crewai_tools import (
# #     SerperDevTool,
# #     WebsiteSearchTool,
# #     FileReadTool,
# #     FileWriterTool
# # )
# # from agents.planner_agent import PlannerAgent
# # from agents.researcher_agent import ResearcherAgent
# # from agents.executor_agent import ExecutorAgent
# # from agents.reviewer_agent import ReviewerAgent
# # from tasks.task_definitions import TaskDefinitions
# # import os

# # class TaskCrewOrchestrator:
# #     def __init__(self, config):
# #         self.config = config
# #         self.setup_environment()
        
# #         # Initialize tools
# #         self.search_tool = SerperDevTool()
# #         self.web_tool = WebsiteSearchTool()
# #         self.read_tool = FileReadTool()
# #         self.write_tool = FileWriterTool()
        
# #         # Initialize agents
# #         self.planner = PlannerAgent(self.search_tool, config)
# #         self.researcher = ResearcherAgent(self.search_tool, self.web_tool, config)
# #         self.executor = ExecutorAgent(self.write_tool, config)
# #         self.reviewer = ReviewerAgent(self.read_tool, config)
        
# #         # Create agent instances
# #         self.agents = self._create_agents()
# #         self.tasks = TaskDefinitions(self.agents)
    
# #     def setup_environment(self):
# #         """Setup required directories"""
# #         os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
# #         os.makedirs(self.config.MEMORY_DIR, exist_ok=True)
    
# #     def _create_agents(self):
# #         """Create CrewAI agent instances"""
# #         return {
# #             "planner": Agent(
# #                 role=self.planner.role,
# #                 goal=self.planner.goal,
# #                 backstory=self.planner.backstory,
# #                 tools=[self.search_tool, self.read_tool],
# #                 verbose=self.config.CREW_VERBOSE,
# #                 allow_delegation=True
# #             ),
# #             "researcher": Agent(
# #                 role=self.researcher.role,
# #                 goal=self.researcher.goal,
# #                 backstory=self.researcher.backstory,
# #                 tools=[self.search_tool, self.web_tool, self.read_tool],
# #                 verbose=self.config.CREW_VERBOSE,
# #                 allow_delegation=True
# #             ),
# #             "executor": Agent(
# #                 role=self.executor.role,
# #                 goal=self.executor.goal,
# #                 backstory=self.executor.backstory,
# #                 tools=[self.write_tool, self.read_tool],
# #                 verbose=self.config.CREW_VERBOSE,
# #                 allow_delegation=True
# #             ),
# #             "reviewer": Agent(
# #                 role=self.reviewer.role,
# #                 goal=self.reviewer.goal,
# #                 backstory=self.reviewer.backstory,
# #                 tools=[self.read_tool],
# #                 verbose=self.config.CREW_VERBOSE,
# #                 allow_delegation=False
# #             )
# #         }
    
# #     def create_crew(self, goal: str):
# #         """Create a crew with tasks for the given goal"""
        
# #         # Get tasks for the goal
# #         task_list = self.tasks.get_tasks_for_goal(goal)
        
# #         # Create CrewAI tasks
# #         crew_tasks = []
        
# #         for task_def in task_list:
# #             task = Task(
# #                 description=task_def["description"],
# #                 agent=self.agents[task_def["agent"]],
# #                 expected_output=task_def["expected_output"],
# #                 tools=task_def.get("tools", []),
# #                 async_execution=task_def.get("async", False),
# #                 context=task_def.get("context", [])
# #             )
# #             crew_tasks.append(task)
        
# #         # Create the crew
# #         crew = Crew(
# #             agents=list(self.agents.values()),
# #             tasks=crew_tasks,
# #             process=Process.sequential,
# #             verbose=self.config.CREW_VERBOSE,
# #             memory=True,
# #             cache=True
# #         )
        
# #         return crew
    
# #     def execute_goal(self, goal: str):
# #         """Execute a goal using the crew"""
# #         print(f"🤖 TaskCrew starting execution for: {goal}")
        
# #         try:
# #             # Create crew for this goal
# #             crew = self.create_crew(goal)
            
# #             # Execute the crew
# #             result = crew.kickoff()
            
# #             # Save the result
# #             self._save_execution_result(goal, result)
            
# #             return {
# #                 "success": True,
# #                 "goal": goal,
# #                 "result": str(result),
# #                 "tasks_completed": len(crew.tasks)
# #             }
            
# #         except Exception as e:
# #             print(f"Error executing goal: {e}")
# #             return {
# #                 "success": False,
# #                 "error": str(e),
# #                 "goal": goal
# #             }
    
# #     def _save_execution_result(self, goal: str, result):
# #         """Save execution result to file"""
# #         import json
# #         from datetime import datetime
        
# #         result_data = {
# #             "goal": goal,
# #             "result": str(result),
# #             "timestamp": datetime.now().isoformat(),
# #             "output_dir": self.config.OUTPUT_DIR
# #         }
        
# #         filename = f"memory/execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
# #         with open(filename, 'w') as f:
# #             json.dump(result_data, f, indent=2)
        
# #         return filename








# from crewai import Agent, Task, Crew, Process
# from tools import search_tool, browse_tool, create_file_tool, read_file_tool, execute_code_tool
# from agents.planner_agent import PlannerAgent
# from agents.researcher_agent import ResearcherAgent
# from agents.executor_agent import ExecutorAgent
# from agents.reviewer_agent import ReviewerAgent
# import os

# class TaskCrewOrchestrator:
#     def __init__(self, config):
#         self.config = config
#         self.setup_environment()
        
#         # Initialize agents
#         self.planner = PlannerAgent(config)
#         self.researcher = ResearcherAgent(config)
#         self.executor = ExecutorAgent(config)
#         self.reviewer = ReviewerAgent(config)
        
#         # Create agent instances
#         self.agents = self._create_agents()
    
#     def setup_environment(self):
#         os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
#         os.makedirs(self.config.MEMORY_DIR, exist_ok=True)
    
#     def _create_agents(self):
#         return {
#             "planner": Agent(
#                 role=self.planner.role,
#                 goal=self.planner.goal,
#                 backstory=self.planner.backstory,
#                 tools=[search_tool, read_file_tool],
#                 verbose=self.config.CREW_VERBOSE,
#                 allow_delegation=True
#             ),
#             "researcher": Agent(
#                 role=self.researcher.role,
#                 goal=self.researcher.goal,
#                 backstory=self.researcher.backstory,
#                 tools=[search_tool, browse_tool, read_file_tool],
#                 verbose=self.config.CREW_VERBOSE,
#                 allow_delegation=True
#             ),
#             "executor": Agent(
#                 role=self.executor.role,
#                 goal=self.executor.goal,
#                 backstory=self.executor.backstory,
#                 tools=[create_file_tool, read_file_tool, execute_code_tool],
#                 verbose=self.config.CREW_VERBOSE,
#                 allow_delegation=True
#             ),
#             "reviewer": Agent(
#                 role=self.reviewer.role,
#                 goal=self.reviewer.goal,
#                 backstory=self.reviewer.backstory,
#                 tools=[read_file_tool],
#                 verbose=self.config.CREW_VERBOSE,
#                 allow_delegation=False
#             )
#         }
    
#     def create_crew(self, goal: str):
#         tasks = [
#             Task(
#                 description=f"Plan this goal: {goal}",
#                 agent=self.agents["planner"],
#                 expected_output="A step-by-step plan",
#             ),
#             Task(
#                 description=f"Research information for: {goal}",
#                 agent=self.agents["researcher"],
#                 expected_output="Research findings",
#                 context=["planner"]
#             ),
#             Task(
#                 description=f"Execute the plan for: {goal}",
#                 agent=self.agents["executor"],
#                 expected_output="Completed deliverables",
#                 context=["researcher"]
#             ),
#             Task(
#                 description="Review the outputs",
#                 agent=self.agents["reviewer"],
#                 expected_output="Quality review",
#                 context=["executor"]
#             )
#         ]
        
#         return Crew(
#             agents=list(self.agents.values()),
#             tasks=tasks,
#             process=Process.sequential,
#             verbose=self.config.CREW_VERBOSE
#         )
    
#     def execute_goal(self, goal: str):
#         try:
#             crew = self.create_crew(goal)
#             result = crew.kickoff()
#             return {
#                 "success": True,
#                 "goal": goal,
#                 "result": str(result)
#             }
#         except Exception as e:
#             return {
#                 "success": False,
#                 "error": str(e)
#             }
        


from crewai import Agent, Task, Crew, Process
from tools import search_tool, browse_tool, create_file_tool, read_file_tool, execute_code_tool
from agents.planner_agent import PlannerAgent
from agents.researcher_agent import ResearcherAgent
from agents.executor_agent import ExecutorAgent
from agents.reviewer_agent import ReviewerAgent
from tasks.task_definitions import TaskDefinitions
import os

class TaskCrewOrchestrator:
    def __init__(self, config):
        self.config = config
        self.setup_environment()
        
        # Initialize agents
        self.planner = PlannerAgent(config)
        self.researcher = ResearcherAgent(config)
        self.executor = ExecutorAgent(config)
        self.reviewer = ReviewerAgent(config)
        
        # Create agent instances
        self.agents = self._create_agents()
        self.tasks_def = TaskDefinitions(self.agents)  # Pass agents dict
    
    def setup_environment(self):
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.config.MEMORY_DIR, exist_ok=True)
    
    def _create_agents(self):
        return {
            "planner": Agent(
                role=self.planner.role,
                goal=self.planner.goal,
                backstory=self.planner.backstory,
                tools=[search_tool, read_file_tool],
                verbose=self.config.CREW_VERBOSE,
                allow_delegation=True
            ),
            "researcher": Agent(
                role=self.researcher.role,
                goal=self.researcher.goal,
                backstory=self.researcher.backstory,
                tools=[search_tool, browse_tool, read_file_tool],
                verbose=self.config.CREW_VERBOSE,
                allow_delegation=True
            ),
            "executor": Agent(
                role=self.executor.role,
                goal=self.executor.goal,
                backstory=self.executor.backstory,
                tools=[create_file_tool, read_file_tool, execute_code_tool],
                verbose=self.config.CREW_VERBOSE,
                allow_delegation=True
            ),
            "reviewer": Agent(
                role=self.reviewer.role,
                goal=self.reviewer.goal,
                backstory=self.reviewer.backstory,
                tools=[read_file_tool],
                verbose=self.config.CREW_VERBOSE,
                allow_delegation=False
            )
        }
    
    def create_crew(self, goal: str):
        # Get task definitions
        task_defs = self.tasks_def.get_tasks_for_goal(goal)
        
        # Convert to CrewAI Task objects
        tasks = []
        for task_def in task_defs:
            task = Task(
                description=task_def["description"],
                agent=self.agents[task_def["agent"]],  # Get agent object from dict
                expected_output=task_def["expected_output"],
            )
            tasks.append(task)
        
        return Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=self.config.CREW_VERBOSE
        )
    
    def execute_goal(self, goal: str):
        try:
            crew = self.create_crew(goal)
            result = crew.kickoff()
            return {
                "success": True,
                "goal": goal,
                "result": str(result)
            }
        except Exception as e:
            print(f"Detailed error: {str(e)}")  # For debugging
            return {
                "success": False,
                "error": str(e)
            }