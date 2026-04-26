import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  intent?: string;
  workflow?: string;
  confidence?: string;
}

export interface ChatState {
  sessionId: string;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  workflows: any[];
  currentWorkflow: string | null;

  // Actions
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setWorkflows: (workflows: any[]) => void;
  setCurrentWorkflow: (workflow: string) => void;
  clearMessages: () => void;
  initSession: () => void;
}

const useChat = create<ChatState>(
  devtools((set) => ({
    sessionId: generateSessionId(),
    messages: [],
    isLoading: false,
    error: null,
    workflows: [],
    currentWorkflow: null,

    addMessage: (message) =>
      set((state) => ({
        messages: [...state.messages, message],
      })),

    setLoading: (loading) =>
      set(() => ({
        isLoading: loading,
      })),

    setError: (error) =>
      set(() => ({
        error,
      })),

    setWorkflows: (workflows) =>
      set(() => ({
        workflows,
      })),

    setCurrentWorkflow: (workflow) =>
      set(() => ({
        currentWorkflow: workflow,
      })),

    clearMessages: () =>
      set(() => ({
        messages: [],
        error: null,
      })),

    initSession: () =>
      set(() => ({
        sessionId: generateSessionId(),
        messages: [],
      })),
  }))
);

function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export default useChat;