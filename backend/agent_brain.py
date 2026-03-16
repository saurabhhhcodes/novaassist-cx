import os
import json
import decimal
import re
from typing import List, Dict, Any, Callable
from nova_client import NovaClient
from email_service import EmailService
from crm_service import CRMService
from ticket_service import TicketService
from memory_service import MemoryService
from kb_service import KnowledgeBaseService
from adapters.order_adapter import SqliteOrderAdapter
from adapters.dynamo_order_adapter import DynamoDBOrderAdapter

class AgentBrain:
    def __init__(self, nova: NovaClient):
        self.nova = nova
        self.email = EmailService()
        self.crm = CRMService()
        self.tickets = TicketService()
        self.memory = MemoryService()
        self.kb = KnowledgeBaseService(nova)
        
        # Enterprise Data Adapters
        mock_mode = os.getenv("MOCK_SERVICES", "true").lower() == "true"
        print(f"AgentBrain: Initializing with MOCK_SERVICES={mock_mode}")
        if mock_mode:
            self.orders = SqliteOrderAdapter()
        else:
            self.orders = DynamoDBOrderAdapter()
        
        # Registry of available tools for Nova Act
        self.tools_schema = [
            {
                "name": "get_order_details",
                "description": "Retrieve full details for a specific order from the enterprise database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "The unique order ID."}
                    },
                    "required": ["order_id"]
                }
            },
            {
                "name": "update_order_status",
                "description": "Update the real-time shipping or fulfillment status in the order database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "The unique order ID."},
                        "status": {"type": "string", "description": "The new status (e.g., SHIPPED, DELIVERED, RETURNED)."}
                    },
                    "required": ["order_id", "status"]
                }
            },
            {
                "name": "process_refund",
                "description": "Initiate a financial refund and update the transaction record.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "The order ID to refund."},
                        "amount": {"type": "number", "description": "The amount to refund."},
                        "reason": {"type": "string", "description": "The reason for the refund."}
                    },
                    "required": ["order_id", "amount", "reason"]
                }
            },
            {
                "name": "check_inventory",
                "description": "Check real-time stock availability in the warehouse.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "The SKU or Product ID."}
                    },
                    "required": ["product_id"]
                }
            },
            {
                "name": "search_knowledge_base",
                "description": "Query the latest product technical manuals and enterprise policy docs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search term."}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "send_email",
                "description": "Dispatch a professional, context-aware support email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "Customer email"},
                        "subject": {"type": "string", "description": "Subject"},
                        "body": {"type": "string", "description": "Content"}
                    },
                    "required": ["recipient", "subject", "body"]
                }
            },
            {
                "name": "create_crm_ticket",
                "description": "Log a formal support engagement in the HubSpot CRM.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Customer email"},
                        "description": {"type": "string", "description": "Issue details"}
                    },
                    "required": ["email", "description"]
                }
            }
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Executes a real tool and returns the observation.
        """
        print(f"AgentBrain: Activating {tool_name}...")
        
        if tool_name == "get_order_details":
            order_id = arguments.get('order_id', '').strip()
            details = self.orders.get_record(order_id)
            if details:
                print(f"📦 [DATABASE]: Pulled live data for {order_id}")
                return json.dumps(details)
            return json.dumps({"status": "error", "message": f"Order {order_id} not found in database."})

        elif tool_name == "update_order_status":
            order_id = arguments.get('order_id', '').strip()
            new_status = arguments.get('status', 'PENDING')
            success = self.orders.update_record(order_id, {"status": new_status})
            if success:
                print(f"📦 [DATABASE]: Record {order_id} committed with status {new_status}")
                return json.dumps({"status": "success", "order_id": order_id, "new_status": new_status})
            return json.dumps({"status": "error", "message": f"Update failed for {order_id}"})

        elif tool_name == "process_refund":
            order_id = arguments.get('order_id', '').strip()
            amount = arguments.get('amount', 0)
            reason = arguments.get('reason', 'Not specified')
            success = self.orders.update_record(order_id, {
                "status": "REFUNDED",
                "issue_history": [{"date": "2026-03-15", "issue": f"Refund of {amount}", "resolution": f"Processed: {reason}"}]
            })
            if success:
                print(f"💰 [FINANCE]: Refund of {amount} processed for {order_id}")
                return json.dumps({"status": "refund_completed", "order_id": order_id, "amount": amount})
            return json.dumps({"status": "error", "message": "Refund failed"})

        elif tool_name == "check_inventory":
            # Real hardware integration would go here. For now, we simulate a warehouse DB lookup
            stock = {"CX-5566": 12, "PROD-123": 45}.get(arguments.get("product_id"), 5)
            return json.dumps({"product_id": arguments.get('product_id'), "quantity": stock, "status": "In Stock" if stock > 0 else "Out of Stock"})

        elif tool_name == "search_knowledge_base":
            results = self.kb.search(arguments.get("query", ""))
            return json.dumps({"results": results})
            
        elif tool_name == "send_email":
            recipient = arguments.get("recipient", "").strip()
            result = self.email.send_support_email(recipient, arguments["subject"], arguments["body"])
            return json.dumps(result)
            
        elif tool_name == "create_crm_ticket":
            # Double commit: HubSpot + Local Persistence
            ticket = self.tickets.create_ticket(arguments["email"], arguments["description"])
            crm_id = await self.crm.create_crm_ticket(arguments["email"], arguments["description"])
            return json.dumps({"ticket_id": ticket["ticket_id"], "crm_id": crm_id, "status": "Logged"})

        return json.dumps({"status": "error", "message": f"Unknown tool: {tool_name}"})

    def _clean_types(self, obj):
        if isinstance(obj, list):
            return [self._clean_types(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self._clean_types(v) for k, v in obj.items()}
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return obj

    async def run_agent_loop(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        The core world-class agentic loop.
        """
        system_prompt = (
            "You are Nova, an Elite Enterprise Support Agent for NovaAssist CX. You operate with mathematical precision.\n"
            "CRITICAL PROTOCOL:\n"
            "1. INTERNAL REASONING: You MUST encapsulate every single thought, plan, or system analysis inside <thinking>...</thinking> tags. This is mandatory for professional voice suppression.\n"
            "2. PROACTIVENESS: Always pull live data from enterprise adapters immediately when a query involves orders, shipping, or inventory.\n"
            "3. DATA-CENTRIC: Reference 'Tracking Numbers', 'Items', and 'Estimated Delivery' dates from the database in all resolutions.\n"
            "4. INDUSTRIAL EMAILS: Use this formal template:\n"
            "   - Subject: [Support Update] Order [Order ID] - [Action Status]\n"
            "   - Body: Dear [Customer Name], I have successfully processed the [Action] for your [Items]. Tracking: [ID]. Delivery: [Date]."
        )
        
        try:
            history = self.memory.get_history(session_id)
            history = self._clean_types(history)
            
            current_msg = {"role": "user", "content": [{"text": user_input or "Continue"}]}
            history.append(current_msg)
            
            # Helper to filter out blank text blocks which cause ValidationException
            def filter_blank_text(msg):
                if "content" in msg:
                    msg["content"] = [c for c in msg["content"] if not ("text" in c and not c["text"].strip())]
                return msg

            history = [filter_blank_text(m) for m in history]
            
            response_msg = self.nova.invoke_nova_act(user_input, self.tools_schema, history=history, system=system_prompt)
            response_msg = self._clean_types(response_msg)
            
            max_iterations = 5
            iterations = 0
            all_text_blocks = []
            
            while iterations < max_iterations:
                for content in response_msg["content"]:
                    if "text" in content:
                        text = content["text"]
                        # Robust suppression of un-tagged reasoning in the final output
                        text = re.sub(r'Internal Reasoning:?.*?\n', '', text, flags=re.IGNORECASE)
                        if text.strip():
                            all_text_blocks.append(text)
                
                has_tool_use = any("toolUse" in content for content in response_msg["content"])
                if not has_tool_use:
                    break
                    
                iterations += 1
                history.append(response_msg)
                
                tool_results_content = []
                for content in response_msg["content"]:
                    if "toolUse" in content:
                        tool_use = content["toolUse"]
                        observation = await self.execute_tool(tool_use["name"], tool_use["input"])
                        
                        tool_results_content.append({
                            "toolResult": {
                                "toolUseId": tool_use["toolUseId"],
                                "content": [{"json": json.loads(observation)}],
                                "status": "success"
                            }
                        })
                
                history.append({"role": "user", "content": tool_results_content})
                response_msg = self.nova.continue_agent_loop(history, self.tools_schema, system=system_prompt)
                response_msg = self._clean_types(response_msg)
            
            final_text = "\n\n".join(all_text_blocks)
            if not final_text:
                final_text = "Fulfillment complete. How else may I assist you?"
                
            history.append(response_msg)
            self.memory.update_history(session_id, [current_msg, response_msg])
            
            return {"response": final_text, "session_id": session_id}
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"response": f"I encountered a system error: {str(e)}", "session_id": session_id}
