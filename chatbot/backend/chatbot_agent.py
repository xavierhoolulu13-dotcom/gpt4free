import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime
from intent_router import IntentRouter, RoutingDecision

class ChatbotAgent:
    """Multi-agent chatbot powered by gpt4free."""
    
    def __init__(self, sheets_backend, intent_router: IntentRouter):
        self.sheets_backend = sheets_backend
        self.intent_router = intent_router
        self.conversations = {}  # In-memory session storage
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """Process message and return structured response."""
        import time
        start_time = time.time()
        
        # Step 1: Route intent
        routing_rules = self.sheets_backend.get_routing_rules()
        decision = self.intent_router.route(message, routing_rules)
        
        # Step 2: Get workflow and agent config
        workflows = self.sheets_backend.get_workflows()
        workflow = next(
            (w for w in workflows if w['id'] == decision.workflow_id),
            None
        )
        
        if not workflow:
            workflow = workflows[0]  # Fallback to first workflow
        
        agents = self.sheets_backend.get_agents(workflow['id'])
        agent = agents[0] if agents else None
        
        # Step 3: Generate response using gpt4free
        response = await self._generate_response(
            message=message,
            workflow=workflow,
            agent=agent,
            session_history=self.conversations.get(session_id, [])
        )
        
        # Step 4: Save to conversation history
        self.conversations.setdefault(session_id, []).append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        self.conversations[session_id].append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat(),
            'workflow_id': decision.workflow_id,
            'intent': decision.intent.value
        })
        
        # Step 5: Log to Google Sheets
        response_time = time.time() - start_time
        self.sheets_backend.save_conversation(
            session_id=session_id,
            user_id=user_id,
            message=message,
            intent=decision.intent.value,
            workflow_id=decision.workflow_id,
            response=response
        )
        self.sheets_backend.log_analytics(
            session_id=session_id,
            intent=decision.intent.value,
            workflow_id=decision.workflow_id,
            response_time=response_time,
            success=True
        )
        
        return {
            'response': response,
            'intent': decision.intent.value,
            'workflow': workflow['name'],
            'confidence': f"{decision.confidence*100:.0f}%",
            'keywords_matched': decision.keywords_matched,
            'response_time': f"{response_time:.2f}s"
        }
    
    async def stream_response(
        self,
        message: str,
        session_id: str,
        user_id: str = "default_user"
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens in real-time."""
        import time
        start_time = time.time()
        
        # Route intent
        routing_rules = self.sheets_backend.get_routing_rules()
        decision = self.intent_router.route(message, routing_rules)
        
        # Get workflow
        workflows = self.sheets_backend.get_workflows()
        workflow = next(
            (w for w in workflows if w['id'] == decision.workflow_id),
            None
        ) or workflows[0]
        
        # Get agent
        agents = self.sheets_backend.get_agents(workflow['id'])
        agent = agents[0] if agents else None
        
        # Build prompt
        system_prompt = agent['system_prompt'] if agent else workflow['system_prompt']
        context = self._build_context(
            message=message,
            workflow=workflow,
            session_history=self.conversations.get(session_id, [])
        )
        
        full_response = ""
        
        # Stream from gpt4free
        async for chunk in self._stream_gpt4free(system_prompt, context, message):
            full_response += chunk
            yield chunk
        
        # Save after streaming completes
        self.conversations.setdefault(session_id, []).append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        self.conversations[session_id].append({
            'role': 'assistant',
            'content': full_response,
            'timestamp': datetime.now().isoformat(),
            'workflow_id': decision.workflow_id,
            'intent': decision.intent.value
        })
        
        # Log analytics
        response_time = time.time() - start_time
        self.sheets_backend.save_conversation(
            session_id=session_id,
            user_id=user_id,
            message=message,
            intent=decision.intent.value,
            workflow_id=decision.workflow_id,
            response=full_response
        )
        self.sheets_backend.log_analytics(
            session_id=session_id,
            intent=decision.intent.value,
            workflow_id=decision.workflow_id,
            response_time=response_time,
            success=True
        )
    
    async def _generate_response(
        self,
        message: str,
        workflow: Dict[str, Any],
        agent: Optional[Dict[str, Any]],
        session_history: list
    ) -> str:
        """Generate response using gpt4free."""
        system_prompt = agent['system_prompt'] if agent else workflow['system_prompt']
        context = self._build_context(message, workflow, session_history)
        
        # Simulate gpt4free call (replace with actual implementation)
        response = f"[{workflow['name']}] I've processed your request about '{message[:50]}...'. "
        response += f"System is using the {workflow['name']} workflow. "
        response += f"Here's how I can help: [detailed response would be generated by LLM]"
        
        return response
    
    async def _stream_gpt4free(
        self,
        system_prompt: str,
        context: str,
        user_message: str
    ) -> AsyncGenerator[str, None]:
        """Stream from gpt4free API."""
        # This would integrate with actual gpt4free library
        # For now, simulating streaming response
        response_chunks = [
            "I'll help you with that. ",
            "Based on your query, ",
            "the best approach is to ",
            "use the specialized workflow ",
            "configured for this intent. ",
            "Here are my recommendations..."
        ]
        
        for chunk in response_chunks:
            yield chunk
            await asyncio.sleep(0.1)  # Simulate streaming delay
    
    def _build_context(
        self,
        message: str,
        workflow: Dict[str, Any],
        session_history: list
    ) -> str:
        """Build context from workflow and conversation history."""
        context = f"Workflow: {workflow['name']}\n"
        context += f"Description: {workflow['description']}\n\n"
        context += "Recent conversation:\n"
        
        for item in session_history[-5:]:  # Last 5 messages
            role = item['role'].upper()
            context += f"{role}: {item['content']}\n"
        
        context += f"USER: {message}\n"
        context += "ASSISTANT:"
        
        return context
    
    def get_session_history(self, session_id: str) -> list:
        """Get conversation history for a session."""
        return self.conversations.get(session_id, [])
    
    def clear_session(self, session_id: str):
        """Clear session history."""
        if session_id in self.conversations:
            del self.conversations[session_id]