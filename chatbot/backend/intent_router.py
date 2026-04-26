import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class Intent(str, Enum):
    SALES = "sales"
    CONTENT = "content"
    DATA = "data"
    GENERAL = "general"

@dataclass
class RoutingDecision:
    intent: Intent
    workflow_id: str
    confidence: float
    keywords_matched: List[str]

class IntentRouter:
    """Intelligent intent classification and routing system."""
    
    def __init__(self):
        self.intent_keywords = {
            Intent.SALES: {
                'keywords': [
                    'lead', 'prospect', 'client', 'customer', 'outreach',
                    'find', 'search', 'qualify', 'b2b', 'saas',
                    'pipeline', 'conversion', 'deal', 'sales', 'revenue',
                    'contact', 'email', 'linkedin', 'database', 'list'
                ],
                'phrases': [
                    'find me leads', 'qualify leads', 'outreach campaign',
                    'lead generation', 'sales pipeline', 'prospect research'
                ],
                'workflow_id': 'aom'
            },
            Intent.CONTENT: {
                'keywords': [
                    'content', 'blog', 'article', 'seo', 'optimize',
                    'improve', 'rewrite', 'quality', 'traffic', 'rank',
                    'keywords', 'meta', 'title', 'description', 'copy',
                    'social', 'post', 'viral', 'engagement', 'reach'
                ],
                'phrases': [
                    'optimize content', 'improve seo', 'rewrite article',
                    'content strategy', 'seo audit', 'blog optimization'
                ],
                'workflow_id': 'cg'
            },
            Intent.DATA: {
                'keywords': [
                    'data', 'process', 'analyze', 'clean', 'transform',
                    'extract', 'parse', 'format', 'csv', 'json',
                    'database', 'report', 'metric', 'insight', 'trend'
                ],
                'phrases': [
                    'process data', 'analyze dataset', 'clean data',
                    'data transformation', 'generate report'
                ],
                'workflow_id': 'general'
            }
        }
    
    def route(self, message: str, routing_rules: List[Dict] = None) -> RoutingDecision:
        """Route user message to appropriate workflow."""
        message_lower = message.lower()
        scores = {intent: {'score': 0, 'keywords': []} for intent in Intent}
        
        # Score each intent based on keyword matches
        for intent, config in self.intent_keywords.items():
            # Check keywords
            for keyword in config['keywords']:
                if keyword in message_lower:
                    scores[intent]['score'] += 1
                    scores[intent]['keywords'].append(keyword)
            
            # Check phrases (higher weight)
            for phrase in config['phrases']:
                if phrase in message_lower:
                    scores[intent]['score'] += 3
                    scores[intent]['keywords'].append(phrase)
        
        # Apply custom routing rules if provided
        if routing_rules:
            for rule in routing_rules:
                if rule['intent_keyword'].lower() in message_lower:
                    matched_intent = self._keyword_to_intent(rule['workflow_id'])
                    if matched_intent:
                        scores[matched_intent]['score'] += rule.get('priority', 0) * 2
        
        # Determine best match
        best_intent = max(scores, key=lambda x: scores[x]['score'])
        best_score = scores[best_intent]['score']
        
        # Calculate confidence
        total_score = sum(s['score'] for s in scores.values())
        confidence = best_score / total_score if total_score > 0 else 0.5
        
        # Default to general if confidence is too low
        if confidence < 0.3:
            best_intent = Intent.GENERAL
            confidence = 0.5
        
        workflow_id = self.intent_keywords[best_intent]['workflow_id']
        keywords_matched = scores[best_intent]['keywords']
        
        return RoutingDecision(
            intent=best_intent,
            workflow_id=workflow_id,
            confidence=min(confidence, 0.99),
            keywords_matched=keywords_matched
        )
    
    def _keyword_to_intent(self, workflow_id: str) -> Intent:
        """Convert workflow_id back to intent."""
        mapping = {v['workflow_id']: k for k, v in self.intent_keywords.items()}
        return mapping.get(workflow_id)
    
    def explain_routing(self, message: str, decision: RoutingDecision) -> Dict:
        """Explain why message was routed to a specific workflow."""
        return {
            'message': message,
            'intent': decision.intent.value,
            'workflow_id': decision.workflow_id,
            'confidence': f"{decision.confidence * 100:.1f}%",
            'keywords_matched': decision.keywords_matched,
            'explanation': f"Routed to {decision.workflow_id} workflow with {decision.confidence*100:.0f}% confidence based on keywords: {', '.join(decision.keywords_matched[:3])}"
        }