import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleSheetsBackend:
    """Google Sheets database interface for chatbot workflows, agents, and conversations."""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, sheets_id: str, credentials_path: Optional[str] = None):
        self.sheets_id = sheets_id
        self.service = self._initialize_sheets(credentials_path)
        self._ensure_sheets_exist()
    
    def _initialize_sheets(self, credentials_path: Optional[str]):
        """Initialize Google Sheets API client."""
        if credentials_path and os.path.exists(credentials_path):
            credentials = Credentials.from_service_account_file(
                credentials_path, scopes=self.SCOPES
            )
        else:
            auth.authenticate_user()
            credentials = auth.default()[0]
        
        return build('sheets', 'v4', credentials=credentials)
    
    def _ensure_sheets_exist(self):
        """Create necessary sheets if they don't exist."""
        required_sheets = [
            'workflows', 'agents', 'conversations', 
            'routing_rules', 'users', 'analytics'
        ]
        
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.sheets_id
            ).execute()
            existing_sheets = [s['properties']['title'] for s in sheet_metadata['sheets']]
            
            for sheet_name in required_sheets:
                if sheet_name not in existing_sheets:
                    self._create_sheet(sheet_name)
                    self._initialize_sheet_headers(sheet_name)
        except HttpError as error:
            print(f'An error occurred: {error}')
    
    def _create_sheet(self, sheet_name: str):
        """Create a new sheet."""
        body = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {'title': sheet_name}
                    }
                }
            ]
        }
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.sheets_id, body=body
        ).execute()
    
    def _initialize_sheet_headers(self, sheet_name: str):
        """Initialize sheet with appropriate headers."""
        headers = {
            'workflows': ['id', 'name', 'description', 'icon', 'color', 'system_prompt', 'created_at'],
            'agents': ['id', 'name', 'workflow_id', 'role', 'system_prompt', 'model', 'created_at'],
            'conversations': ['id', 'session_id', 'user_id', 'message', 'intent', 'workflow_id', 'response', 'timestamp'],
            'routing_rules': ['intent_keyword', 'workflow_id', 'confidence_threshold', 'priority'],
            'users': ['user_id', 'name', 'email', 'created_at', 'last_active'],
            'analytics': ['timestamp', 'session_id', 'intent', 'workflow_id', 'response_time', 'success', 'user_feedback']
        }
        
        if sheet_name in headers:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_id,
                range=f'{sheet_name}!A1',
                valueInputOption='RAW',
                body={'values': [headers[sheet_name]]}
            ).execute()
    
    def get_workflows(self) -> List[Dict[str, Any]]:
        """Fetch all workflows from Google Sheets."""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_id, range='workflows!A2:G'
        ).execute()
        rows = result.get('values', [])
        
        workflows = []
        for row in rows:
            if len(row) >= 7:
                workflows.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'icon': row[3],
                    'color': row[4],
                    'system_prompt': row[5],
                    'created_at': row[6]
                })
        return workflows
    
    def get_agents(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch agents, optionally filtered by workflow."""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_id, range='agents!A2:G'
        ).execute()
        rows = result.get('values', [])
        
        agents = []
        for row in rows:
            if len(row) >= 7:
                agent = {
                    'id': row[0],
                    'name': row[1],
                    'workflow_id': row[2],
                    'role': row[3],
                    'system_prompt': row[4],
                    'model': row[5],
                    'created_at': row[6]
                }
                if workflow_id is None or agent['workflow_id'] == workflow_id:
                    agents.append(agent)
        return agents
    
    def save_conversation(
        self, session_id: str, user_id: str, message: str, 
        intent: str, workflow_id: str, response: str
    ):
        """Save conversation to Google Sheets."""
        values = [[
            f"conv_{session_id}_{datetime.now().timestamp()}",
            session_id,
            user_id,
            message,
            intent,
            workflow_id,
            response,
            datetime.now().isoformat()
        ]]
        
        self.service.spreadsheets().values().append(
            spreadsheetId=self.sheets_id,
            range='conversations!A:H',
            valueInputOption='RAW',
            body={'values': values}
        ).execute()
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_id, range='conversations!A2:H'
        ).execute()
        rows = result.get('values', [])
        
        history = []
        for row in reversed(rows[-limit:]):
            if len(row) >= 8 and row[1] == session_id:
                history.append({
                    'id': row[0],
                    'message': row[3],
                    'intent': row[4],
                    'workflow_id': row[5],
                    'response': row[6],
                    'timestamp': row[7]
                })
        return list(reversed(history))
    
    def log_analytics(
        self, session_id: str, intent: str, workflow_id: str,
        response_time: float, success: bool, user_feedback: str = ""
    ):
        """Log analytics event."""
        values = [[
            datetime.now().isoformat(),
            session_id,
            intent,
            workflow_id,
            response_time,
            'TRUE' if success else 'FALSE',
            user_feedback
        ]]
        
        self.service.spreadsheets().values().append(
            spreadsheetId=self.sheets_id,
            range='analytics!A:G',
            valueInputOption='RAW',
            body={'values': values}
        ).execute()
    
    def get_routing_rules(self) -> List[Dict[str, Any]]:
        """Get intent routing rules."""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_id, range='routing_rules!A2:D'
        ).execute()
        rows = result.get('values', [])
        
        rules = []
        for row in rows:
            if len(row) >= 4:
                rules.append({
                    'intent_keyword': row[0],
                    'workflow_id': row[1],
                    'confidence_threshold': float(row[2]) if row[2] else 0.7,
                    'priority': int(row[3]) if row[3] else 0
                })
        return rules


def initialize_default_workflows(sheets_backend: GoogleSheetsBackend):
    """Initialize default workflows if none exist."""
    workflows = sheets_backend.get_workflows()
    
    if not workflows:
        default_workflows = [
            ['aom', 'AOM Master Flow', 'Sales lead discovery and outreach automation', '🎯', '#f59e0b', 
             'You are an expert sales agent. Help users find and qualify B2B leads. Focus on lead generation, qualification, and outreach strategy.', 
             datetime.now().isoformat()],
            ['cg', 'CG Master Flow', 'Content analysis and optimization', '🛡️', '#10b981', 
             'You are a content guardian. Help users optimize content for SEO, quality, and engagement. Provide specific improvement recommendations.',
             datetime.now().isoformat()],
            ['general', 'General Assistant', 'General support and assistance', '🤖', '#6366f1',
             'You are a helpful AI assistant. Answer user questions and provide guidance on various topics.',
             datetime.now().isoformat()]
        ]
        
        sheets_backend.service.spreadsheets().values().append(
            spreadsheetId=sheets_backend.sheets_id,
            range='workflows!A2:G',
            valueInputOption='RAW',
            body={'values': default_workflows}
        ).execute()