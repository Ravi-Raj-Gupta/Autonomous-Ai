"""
AUTONOMOS - Agentic Operations Manager Backend
Python-based AI Agent System using LangChain, CrewAI, and OpenAI

Setup Instructions:
1. Install dependencies:
   pip install fastapi uvicorn langchain langchain-openai crewai pandas python-dotenv resend

2. Create .env file:
   OPENAI_API_KEY=your_openai_key
   RESEND_API_KEY=your_resend_key (optional)

3. Run server:
   uvicorn autonomos_backend:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from datetime import datetime
import json

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage

# CrewAI imports
from crewai import Agent, Task, Crew, Process

# Resend for email
try:
    import resend
except ImportError:
    resend = None

app = FastAPI(title="AUTONOMOS API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class InventoryItem(BaseModel):
    id: int
    name: str
    stock: int
    reorderPoint: int
    price: float
    vendor: str
    vendorEmail: str
    lastOrder: str
    salesPerDay: float

class AgentDecision(BaseModel):
    decision: str  # AUTO_APPROVE or ESCALATE
    reasoning: str
    vendorEmail: str
    quantity: int
    cost: float
    urgency: str  # LOW, MEDIUM, HIGH, CRITICAL

class AnalysisRequest(BaseModel):
    inventory: List[InventoryItem]
    openai_api_key: str
    resend_api_key: Optional[str] = None
    user_email: Optional[str] = None

# ============================================================================
# AI AGENT SYSTEM - Using LangChain & CrewAI
# ============================================================================

class InventoryAnalysisAgent:
    """LangChain-based agent for inventory analysis"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=api_key
        )
    
    def analyze_item(self, item: InventoryItem) -> Dict:
        """Analyze a single inventory item and make decision"""
        
        days_until_stockout = item.stock / item.salesPerDay if item.salesPerDay > 0 else 999
        recommended_quantity = int(item.salesPerDay * 30)  # 30-day supply
        total_cost = recommended_quantity * item.price
        
        # Determine urgency
        if days_until_stockout <= 2:
            urgency = "CRITICAL"
        elif days_until_stockout <= 5:
            urgency = "HIGH"
        elif days_until_stockout <= 10:
            urgency = "MEDIUM"
        else:
            urgency = "LOW"
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are AUTONOMOS, an AI operations manager for MSMEs. 
Your role is to make intelligent inventory decisions.

Decision Rules:
- AUTO_APPROVE: Routine reorders under $500, normal sales patterns
- ESCALATE: High cost (>$500), unusual situations, first-time orders

Respond ONLY with valid JSON in this format:
{
  "decision": "AUTO_APPROVE" or "ESCALATE",
  "reasoning": "brief 2-3 sentence explanation",
  "vendorEmail": "professional email body for purchase order"
}"""),
            HumanMessage(content=f"""
Analyze this inventory situation:

Item: {item.name}
Current Stock: {item.stock} units
Reorder Point: {item.reorderPoint} units
Daily Sales: {item.salesPerDay} units/day
Days Until Stockout: {days_until_stockout:.1f} days
Recommended Order: {recommended_quantity} units
Total Cost: ${total_cost}
Vendor: {item.vendor}
Urgency: {urgency}

Make your decision now.""")
        ])
        
        response = self.llm.invoke(prompt.format_messages())
        
        # Parse JSON response
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        decision_data = json.loads(content)
        
        return {
            "item": item.name,
            "decision": decision_data["decision"],
            "reasoning": decision_data["reasoning"],
            "vendorEmail": decision_data["vendorEmail"],
            "quantity": recommended_quantity,
            "cost": total_cost,
            "urgency": urgency,
            "vendor": item.vendor,
            "vendorEmailAddress": item.vendorEmail,
            "daysUntilStockout": days_until_stockout
        }


class ProcurementCrew:
    """CrewAI-based multi-agent system for procurement"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # Define agents
        self.inventory_analyst = Agent(
            role='Inventory Analyst',
            goal='Analyze inventory levels and predict stockouts',
            backstory="""You are an expert in inventory management with 15 years 
            of experience in retail operations. You excel at predicting demand 
            and optimizing stock levels.""",
            verbose=True,
            allow_delegation=False,
            llm=ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)
        )
        
        self.procurement_manager = Agent(
            role='Procurement Manager',
            goal='Make cost-effective purchasing decisions',
            backstory="""You are a procurement specialist who negotiates with 
            vendors and ensures timely deliveries while minimizing costs.""",
            verbose=True,
            allow_delegation=False,
            llm=ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)
        )
        
        self.risk_assessor = Agent(
            role='Risk Assessment Officer',
            goal='Evaluate financial and operational risks',
            backstory="""You assess risks in business decisions, focusing on 
            cash flow, vendor reliability, and operational continuity.""",
            verbose=True,
            allow_delegation=False,
            llm=ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)
        )
    
    def analyze_inventory_situation(self, items: List[InventoryItem]) -> Dict:
        """Use crew to analyze entire inventory situation"""
        
        low_stock_items = [item for item in items if item.stock <= item.reorderPoint]
        
        if not low_stock_items:
            return {
                "summary": "All inventory levels are healthy",
                "critical_items": [],
                "recommended_actions": []
            }
        
        # Create analysis task
        analysis_task = Task(
            description=f"""Analyze these low-stock items and provide recommendations:
            
            {json.dumps([item.dict() for item in low_stock_items], indent=2)}
            
            Provide:
            1. Overall inventory health assessment
            2. Critical items requiring immediate action
            3. Recommended procurement strategy""",
            agent=self.inventory_analyst,
            expected_output="Detailed inventory analysis with recommendations"
        )
        
        # Create procurement task
        procurement_task = Task(
            description="""Based on the inventory analysis, create a procurement plan with:
            1. Items to order immediately
            2. Quantities and estimated costs
            3. Vendor communication strategy""",
            agent=self.procurement_manager,
            expected_output="Procurement plan with action items"
        )
        
        # Create risk assessment task
        risk_task = Task(
            description="""Assess risks in the procurement plan:
            1. Financial risks (cash flow impact)
            2. Operational risks (stockout probability)
            3. Vendor risks (reliability, delivery times)
            
            Recommend which decisions can be auto-approved vs need escalation.""",
            agent=self.risk_assessor,
            expected_output="Risk assessment with approval recommendations"
        )
        
        # Create and run crew
        crew = Crew(
            agents=[self.inventory_analyst, self.procurement_manager, self.risk_assessor],
            tasks=[analysis_task, procurement_task, risk_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        
        return {
            "summary": str(result),
            "critical_items": [item.name for item in low_stock_items],
            "analysis_timestamp": datetime.now().isoformat()
        }


# ============================================================================
# EMAIL AUTOMATION
# ============================================================================

class EmailAutomation:
    """Handle automated email sending via Resend"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key and resend:
            resend.api_key = api_key
    
    def send_vendor_email(self, decision: Dict, user_email: str) -> Dict:
        """Send email to vendor (or user for demo)"""
        
        if not self.api_key or not resend:
            return {
                "success": True,
                "simulated": True,
                "message": "Email simulated (Resend not configured)"
            }
        
        try:
            email_html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">AUTONOMOS Purchase Order</h1>
                </div>
                <div style="background: white; padding: 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #1f2937;">Purchase Order Request</h2>
                    <p style="color: #4b5563;">Dear {decision['vendor']},</p>
                    
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 10px 0; color: #6b7280; font-weight: bold;">Item:</td>
                                <td style="padding: 10px 0; color: #1f2937;">{decision['item']}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; color: #6b7280; font-weight: bold;">Quantity:</td>
                                <td style="padding: 10px 0; color: #1f2937;">{decision['quantity']} units</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; color: #6b7280; font-weight: bold;">Estimated Cost:</td>
                                <td style="padding: 10px 0; color: #1f2937; font-size: 18px; font-weight: bold;">${decision['cost']}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; color: #6b7280; font-weight: bold;">Urgency:</td>
                                <td style="padding: 10px 0;">
                                    <span style="background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">
                                        {decision['urgency']}
                                    </span>
                                </td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #eff6ff; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0;">
                        <p style="margin: 0; color: #1e40af; font-size: 14px;">
                            <strong>Message:</strong><br>
                            {decision['vendorEmail']}
                        </p>
                    </div>
                    
                    <p style="color: #4b5563; margin-top: 30px;">
                        Please confirm availability and estimated delivery timeline at your earliest convenience.
                    </p>
                    
                    <p style="color: #4b5563;">
                        Best regards,<br>
                        <strong>AUTONOMOS AI Operations Manager</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    
                    <p style="color: #9ca3af; font-size: 12px; text-align: center;">
                        This email was automatically generated by AUTONOMOS<br>
                        Agentic Operations Manager for MSMEs
                    </p>
                </div>
            </div>
            """
            
            params = {
                "from": "AUTONOMOS <onboarding@resend.dev>",
                "to": [user_email],
                "subject": f"Purchase Order: {decision['item']} - {decision['urgency']} Priority",
                "html": email_html
            }
            
            email = resend.Emails.send(params)
            
            return {
                "success": True,
                "simulated": False,
                "email_id": email.get('id'),
                "message": "Email sent successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "simulated": False,
                "error": str(e),
                "message": f"Email failed: {str(e)}"
            }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "AUTONOMOS Backend",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "LangChain-based inventory analysis",
            "CrewAI multi-agent procurement system",
            "Automated email via Resend",
            "Real-time decision making"
        ]
    }

@app.post("/analyze/simple")
async def analyze_inventory_simple(request: AnalysisRequest):
    """Simple LangChain-based analysis (faster for demos)"""
    try:
        agent = InventoryAnalysisAgent(request.openai_api_key)
        email_automation = EmailAutomation(request.resend_api_key)
        
        results = []
        low_stock_items = [item for item in request.inventory if item.stock <= item.reorderPoint]
        
        for item in low_stock_items:
            decision = agent.analyze_item(item)
            
            # Send email if auto-approved
            if decision["decision"] == "AUTO_APPROVE" and request.user_email:
                email_result = email_automation.send_vendor_email(decision, request.user_email)
                decision["emailStatus"] = email_result
            
            results.append(decision)
        
        return {
            "success": True,
            "method": "langchain",
            "decisions": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/crew")
async def analyze_inventory_crew(request: AnalysisRequest):
    """CrewAI-based multi-agent analysis (more thorough, slower)"""
    try:
        crew = ProcurementCrew(request.openai_api_key)
        
        # Get high-level analysis from crew
        crew_analysis = crew.analyze_inventory_situation(request.inventory)
        
        # Then get individual decisions using LangChain agent
        agent = InventoryAnalysisAgent(request.openai_api_key)
        email_automation = EmailAutomation(request.resend_api_key)
        
        decisions = []
        low_stock_items = [item for item in request.inventory if item.stock <= item.reorderPoint]
        
        for item in low_stock_items:
            decision = agent.analyze_item(item)
            
            if decision["decision"] == "AUTO_APPROVE" and request.user_email:
                email_result = email_automation.send_vendor_email(decision, request.user_email)
                decision["emailStatus"] = email_result
            
            decisions.append(decision)
        
        return {
            "success": True,
            "method": "crewai",
            "crew_analysis": crew_analysis,
            "decisions": decisions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/email/send")
async def send_email(decision: Dict, user_email: str, resend_api_key: Optional[str] = None):
    """Send vendor email manually"""
    try:
        email_automation = EmailAutomation(resend_api_key)
        result = email_automation.send_vendor_email(decision, user_email)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)