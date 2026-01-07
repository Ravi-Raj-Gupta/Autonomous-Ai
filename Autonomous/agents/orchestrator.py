# 1. Main Decision Making
# agents/orchestrator.py
import asyncio
from typing import Dict, List, Any
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from dataclasses import dataclass
from enum import Enum
import json

class BusinessEventType(Enum):
    """Types of business events the agent monitors"""
    INVENTORY_LOW = "inventory_low"
    SALES_SPIKE = "sales_spike"
    VENDOR_DELAY = "vendor_delay"
    STAFF_SHORTAGE = "staff_shortage"
    PAYMENT_DUE = "payment_due"
    CASH_FLOW_WARNING = "cash_flow_warning"
    SEASONAL_TREND = "seasonal_trend"

@dataclass
class BusinessState:
    """Central state representation"""
    inventory_levels: Dict[str, float]  # product_id -> days_of_supply
    sales_velocity: Dict[str, float]    # product_id -> units/day
    vendor_performance: Dict[str, float] # vendor_id -> on_time_percentage
    staff_availability: Dict[str, List[str]]  # role -> available_employees
    pending_orders: List[Dict]
    cash_balance: float
    upcoming_bills: List[Dict]
    recent_alerts: List[Dict]
    
class AutonomousOrchestrator:
    """
    Main agent that coordinates all operations autonomously
    """
    
    def __init__(self, business_id: str):
        self.business_id = business_id
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.1  # Low for consistent decisions
        )
        
        # Initialize specialized agents
        self.inventory_agent = InventoryAgent()
        self.procurement_agent = ProcurementAgent()
        self.staffing_agent = StaffingAgent()
        self.finance_agent = FinanceAgent()
        self.alert_agent = AlertAgent()
        
        # Operational memory
        self.decision_log = []
        self.state_history = []
        
        # Business rules
        self.rules = self._load_business_rules()
        
        # Build the agent graph
        self.workflow = self._build_agent_graph()
    
    def _load_business_rules(self) -> Dict:
        """Load MSME-specific business rules"""
        return {
            "inventory": {
                "reorder_point": 7,  # days of supply
                "safety_stock": 3,   # days
                "max_stock": 30,     # days
                "fast_moving_threshold": 20  # units/day
            },
            "procurement": {
                "preferred_vendors": ["vendor_a", "vendor_b"],
                "payment_terms": "net_30",
                "min_order_value": 1000,
                "bulk_discount_threshold": 10000
            },
            "staffing": {
                "min_shift_coverage": 2,
                "overtime_threshold": 10,  # hours/week
                "skill_matrix": {}  # employee_id -> [skills]
            },
            "finance": {
                "cash_reserve_days": 30,
                "credit_limit_utilization": 0.7,
                "invoice_due_days": 30
            }
        }
    
    def _build_agent_graph(self):
        """Build LangGraph for autonomous decision flow"""
        
        from langgraph.graph import StateGraph
        
        workflow = StateGraph(BusinessState)
        
        # Define nodes (agents)
        workflow.add_node("monitor", self._monitor_operations)
        workflow.add_node("analyze", self._analyze_situations)
        workflow.add_node("decide", self._make_decisions)
        workflow.add_node("execute", self._execute_actions)
        workflow.add_node("log", self._log_decisions)
        
        # Define edges (flow)
        workflow.add_edge("monitor", "analyze")
        workflow.add_edge("analyze", "decide")
        workflow.add_edge("decide", "execute")
        workflow.add_edge("execute", "log")
        workflow.add_edge("log", END)
        
        # Add conditional edges for human escalation
        workflow.add_conditional_edges(
            "decide",
            self._requires_human_approval,
            {
                "human": "alert_agent",
                "auto": "execute"
            }
        )
        
        workflow.set_entry_point("monitor")
        
        return workflow.compile()
    
    async def _monitor_operations(self, state: BusinessState) -> BusinessState:
        """
        Continuously monitor all business operations
        Returns: Updated state with new events detected
        """
        print(f"[{datetime.now()}] 🔍 Monitoring operations...")
        
        # Monitor inventory
        inventory_events = await self.inventory_agent.monitor(state.inventory_levels)
        
        # Monitor sales
        sales_events = await self._monitor_sales_trends(state.sales_velocity)
        
        # Monitor vendors
        vendor_events = await self.procurement_agent.monitor_vendors(
            state.vendor_performance
        )
        
        # Monitor staffing
        staff_events = await self.staffing_agent.monitor_availability(
            state.staff_availability
        )
        
        # Monitor finances
        finance_events = await self.finance_agent.monitor_cash_flow(
            state.cash_balance,
            state.upcoming_bills
        )
        
        # Combine all events
        all_events = inventory_events + sales_events + vendor_events + staff_events + finance_events
        
        # Update state with detected events
        state.recent_alerts = all_events
        
        return state
    
    async def _analyze_situations(self, state: BusinessState) -> BusinessState:
        """
        Analyze detected events and calculate impact
        """
        print(f"[{datetime.now()}] 🧠 Analyzing {len(state.recent_alerts)} events...")
        
        analysis_results = []
        
        for event in state.recent_alerts:
            # Use LLM to analyze impact and urgency
            analysis_prompt = f"""
            As a business operations manager, analyze this event:
            Event: {event['type']}
            Details: {event['details']}
            Current Business State:
            - Cash balance: ${state.cash_balance}
            - Inventory levels: {state.inventory_levels}
            - Staff available: {len(state.staff_availability.get('warehouse', []))}
            
            Analyze:
            1. Business impact (High/Medium/Low)
            2. Urgency (Immediate/24h/48h/Week)
            3. Potential cascading effects
            4. Recommended actions
            
            Return as JSON.
            """
            
            response = await self.llm.ainvoke(analysis_prompt)
            analysis = json.loads(response.content)
            
            analysis_results.append({
                **event,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            })
        
        # Store analysis in state
        state.recent_alerts = analysis_results
        
        return state
    
    async def _make_decisions(self, state: BusinessState) -> BusinessState:
        """
        Autonomous decision-making based on analysis
        """
        print(f"[{datetime.now()}] ⚡ Making decisions...")
        
        decisions = []
        
        for alert in state.recent_alerts:
            if alert['analysis']['urgency'] == 'Immediate':
                # Make immediate autonomous decisions
                decision = await self._make_autonomous_decision(alert, state)
                decisions.append(decision)
            elif alert['analysis']['business_impact'] == 'High':
                # For high-impact decisions, check if autonomous action is allowed
                if self._can_act_autonomously(alert):
                    decision = await self._make_autonomous_decision(alert, state)
                    decisions.append(decision)
                else:
                    # Flag for human approval
                    decisions.append({
                        "type": "requires_human",
                        "alert": alert,
                        "recommended_action": alert['analysis']['recommended_actions'][0]
                    })
        
        # Add decisions to state
        state.recent_alerts = decisions
        
        return state
    
    async def _execute_actions(self, state: BusinessState) -> BusinessState:
        """
        Execute autonomous actions
        """
        print(f"[{datetime.now()}] 🚀 Executing actions...")
        
        executed_actions = []
        
        for decision in state.recent_alerts:
            if decision['type'] != 'requires_human':
                # Execute autonomous action
                action_result = await self._execute_single_action(decision, state)
                executed_actions.append(action_result)
                
                # Update business state based on action
                state = self._update_state_from_action(state, action_result)
        
        return state
    
    def _requires_human_approval(self, state: BusinessState) -> str:
        """
        Determine if human approval is needed
        """
        for decision in state.recent_alerts:
            if decision['type'] == 'requires_human':
                return "human"
        return "auto"
    
    async def run_autonomous_cycle(self, initial_state: BusinessState):
        """
        Run one complete cycle of autonomous operations
        """
        print(f"\n{'='*60}")
        print(f"🔄 AUTONOMOUS OPERATIONS CYCLE - {datetime.now()}")
        print(f"{'='*60}")
        
        # Run the workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        # Log cycle completion
        self.decision_log.append({
            "cycle_id": len(self.decision_log) + 1,
            "timestamp": datetime.now().isoformat(),
            "decisions_made": len([d for d in final_state.recent_alerts 
                                  if d.get('type') != 'requires_human']),
            "human_escalations": len([d for d in final_state.recent_alerts 
                                     if d.get('type') == 'requires_human']),
            "state_snapshot": {
                "cash_balance": final_state.cash_balance,
                "inventory_items": len(final_state.inventory_levels),
                "pending_orders": len(final_state.pending_orders)
            }
        })
        
        return final_state
    
    async def start_continuous_monitoring(self, interval_minutes: int = 5):
        """
        Start continuous autonomous monitoring
        """
        print(f"🚀 Starting continuous monitoring (every {interval_minutes} minutes)")
        
        while True:
            try:
                # Get current state from ERP
                current_state = await self._fetch_current_state()
                
                # Run autonomous cycle
                await self.run_autonomous_cycle(current_state)
                
                # Wait for next cycle
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                print(f"❌ Error in monitoring cycle: {e}")
                await self.alert_agent.send_alert(
                    f"Autonomous system error: {str(e)}",
                    priority="high"
                )
                await asyncio.sleep(60)  # Wait 1 minute before retry