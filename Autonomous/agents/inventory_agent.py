# 2. Inventory Management
# agents/inventory_agent.py
from ast import Dict
from datetime import datetime
from typing import List
from langchain_openai import ChatOpenAI
from scidatetime import timedelta


class InventoryAgent:
    """
    Autonomous inventory management agent
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo")
        self.reorder_history = []
        
    async def monitor(self, inventory_levels: Dict[str, float]) -> List[Dict]:
        """
        Monitor inventory levels and detect issues
        """
        events = []
        
        for product_id, days_of_supply in inventory_levels.items():
            # Check if reorder is needed
            if days_of_supply <= 7:  # 7 days reorder point
                events.append({
                    "type": "inventory_low",
                    "product_id": product_id,
                    "current_stock": days_of_supply,
                    "details": f"Only {days_of_supply} days of supply left",
                    "severity": "high" if days_of_supply <= 3 else "medium"
                })
            
            # Check for excess inventory
            elif days_of_supply >= 60:  # 60 days max
                events.append({
                    "type": "inventory_high",
                    "product_id": product_id,
                    "current_stock": days_of_supply,
                    "details": f"Excess inventory: {days_of_supply} days supply",
                    "severity": "medium"
                })
        
        return events
    
    async def calculate_reorder_quantity(self, product_id: str, 
                                        sales_velocity: float,
                                        lead_time_days: int = 7) -> Dict:
        """
        Calculate optimal reorder quantity using EOQ model
        """
        # Economic Order Quantity formula
        annual_demand = sales_velocity * 365
        ordering_cost = 50  # Fixed cost per order (can be configured)
        holding_cost_rate = 0.20  # 20% of product cost
        unit_cost = await self._get_product_cost(product_id)
        
        # EOQ Formula
        eoq = ((2 * annual_demand * ordering_cost) / 
               (holding_cost_rate * unit_cost)) ** 0.5
        
        # Adjust for safety stock
        safety_stock = sales_velocity * (lead_time_days * 1.5)  # 50% buffer
        
        reorder_quantity = max(eoq, safety_stock)
        
        return {
            "product_id": product_id,
            "economic_order_quantity": round(eoq, 2),
            "safety_stock": round(safety_stock, 2),
            "recommended_order": round(reorder_quantity),
            "expected_delivery_date": (
                datetime.now() + timedelta(days=lead_time_days)
            ).strftime("%Y-%m-%d")
        }
    
    async def create_purchase_order(self, product_id: str, quantity: float) -> Dict:
        """
        Autonomous creation of purchase order
        """
        # Get product details
        product_details = await self._get_product_details(product_id)
        
        # Select vendor (prefers reliable ones)
        vendor = await self._select_vendor(product_id)
        
        # Generate PO
        po_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{len(self.reorder_history)+1:03d}"
        
        purchase_order = {
            "po_number": po_number,
            "date": datetime.now().isoformat(),
            "vendor_id": vendor['id'],
            "vendor_name": vendor['name'],
            "items": [{
                "product_id": product_id,
                "description": product_details['name'],
                "quantity": quantity,
                "unit_price": product_details['cost'],
                "total": quantity * product_details['cost']
            }],
            "total_amount": quantity * product_details['cost'],
            "terms": "Net 30",
            "status": "pending"
        }
        
        # Log the PO
        self.reorder_history.append({
            **purchase_order,
            "decision_reason": "Autonomous reorder based on inventory levels"
        })
        
        return purchase_order
    
    async def _select_vendor(self, product_id: str) -> Dict:
        """
        Intelligently select vendor based on performance
        """
        # Get vendor performance data
        vendors = await self._get_available_vendors(product_id)
        
        if not vendors:
            raise Exception(f"No vendors found for {product_id}")
        
        # Score vendors based on multiple factors
        scored_vendors = []
        for vendor in vendors:
            score = 0
            
            # On-time delivery (40% weight)
            score += vendor.get('on_time_percentage', 0) * 0.4
            
            # Price competitiveness (30% weight)
            best_price = min(v['price'] for v in vendors)
            price_score = (best_price / vendor['price']) * 100
            score += price_score * 0.3
            
            # Quality rating (20% weight)
            score += vendor.get('quality_rating', 5) * 20 * 0.2
            
            # Payment terms (10% weight)
            if vendor.get('payment_terms') == 'net_60':
                score += 10
            elif vendor.get('payment_terms') == 'net_30':
                score += 8
            else:
                score += 5
            
            scored_vendors.append({**vendor, "score": score})
        
        # Select best vendor
        best_vendor = max(scored_vendors, key=lambda x: x['score'])
        
        return best_vendor