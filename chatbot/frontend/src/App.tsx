import { useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import useChat from './store/chat';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const { setWorkflows, initSession } = useChat();

  useEffect(() => {
    initSession();
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      const response = await fetch(`${API_BASE}/workflows`);
      if (response.ok) {
        const data = await response.json();
        setWorkflows(data.workflows);
      }
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-[#08080f]">
      {/* Header */}
      <header className="border-b border-white/5 bg-[#08080f]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-sm font-bold text-white">
              N8
            </div>
            <div>
              <h1 className="text-white font-bold text-sm">n8n Chatbot</h1>
              <p className="text-white/30 text-xs">Workflow Automation AI</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-white/40 text-xs">Connected</span>
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col max-w-6xl mx-auto w-full">
        <ChatWindow />
      </main>
    </div>
  );
}

export default App;