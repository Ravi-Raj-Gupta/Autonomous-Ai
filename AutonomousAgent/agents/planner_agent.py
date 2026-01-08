# class PlannerAgent:
#     def __init__(self, search_tool, config):
#         self.search_tool = search_tool
#         self.config = config
        
#         self.role = """Senior Planning Strategist"""
        
#         self.goal = """Break down complex goals into actionable, sequential tasks 
#         that can be executed by specialized agents"""
        
#         self.backstory = """You are a veteran project manager with 20+ years of 
#         experience in breaking down complex objectives into executable steps. 
#         You're known for your meticulous planning and ability to anticipate 
#         dependencies and potential roadblocks. You work with researchers, 
#         executors, and reviewers to ensure goals are properly decomposed."""
    
#     def plan_goal(self, goal: str) -> list:
#         """Generate a plan for the given goal"""
#         # This would typically use an LLM call via CrewAI
#         # For demo, return a structured plan
#         return self._generate_plan_structure(goal)
    
#     def _generate_plan_structure(self, goal: str) -> list:
#         """Generate a plan structure based on goal type"""
#         goal_lower = goal.lower()
        
#         if any(word in goal_lower for word in ['research', 'find', 'search']):
#             return self._research_plan(goal)
#         elif any(word in goal_lower for word in ['create', 'build', 'make']):
#             return self._creation_plan(goal)
#         elif any(word in goal_lower for word in ['analyze', 'process', 'data']):
#             return self._analysis_plan(goal)
#         else:
#             return self._generic_plan(goal)
    
#     def _research_plan(self, goal: str) -> list:
#         return [
#             {
#                 "agent": "researcher",
#                 "description": f"Research comprehensive information about: {goal}",
#                 "expected_output": "Detailed research report with sources"
#             },
#             {
#                 "agent": "executor",
#                 "description": "Create a well-structured summary document",
#                 "expected_output": "Professional summary document"
#             },
#             {
#                 "agent": "reviewer",
#                 "description": "Review and validate the research quality",
#                 "expected_output": "Quality assessment report"
#             }
#         ]
    
#     def _creation_plan(self, goal: str) -> list:
#         return [
#             {
#                 "agent": "researcher",
#                 "description": f"Research best practices and requirements for: {goal}",
#                 "expected_output": "Requirements and best practices document"
#             },
#             {
#                 "agent": "executor",
#                 "description": f"Create the requested output for: {goal}",
#                 "expected_output": "Completed output file/deliverable"
#             },
#             {
#                 "agent": "reviewer",
#                 "description": "Review the created output for quality",
#                 "expected_output": "Quality review report"
#             }
#         ]
    
#     def _analysis_plan(self, goal: str) -> list:
#         return [
#             {
#                 "agent": "researcher",
#                 "description": "Research analysis methods and tools",
#                 "expected_output": "Analysis methodology document"
#             },
#             {
#                 "agent": "executor",
#                 "description": f"Perform analysis for: {goal}",
#                 "expected_output": "Analysis results and insights"
#             },
#             {
#                 "agent": "reviewer",
#                 "description": "Validate analysis methodology and results",
#                 "expected_output": "Validation report"
#             }
#         ]
    
#     def _generic_plan(self, goal: str) -> list:
#         return [
#             {
#                 "agent": "researcher",
#                 "description": f"Research information about: {goal}",
#                 "expected_output": "Research findings"
#             },
#             {
#                 "agent": "executor",
#                 "description": f"Execute actions for: {goal}",
#                 "expected_output": "Execution results"
#             },
#             {
#                 "agent": "reviewer",
#                 "description": "Review the completed work",
#                 "expected_output": "Review report"
#             }
#         ]



class PlannerAgent:
    def __init__(self, config):
        self.config = config
        self.role = "Senior Planning Strategist"
        self.goal = "Break down goals into actionable tasks"
        self.backstory = "Expert project manager with 20+ years experience"
