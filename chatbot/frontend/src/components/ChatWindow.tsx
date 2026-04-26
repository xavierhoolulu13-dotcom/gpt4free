import React, { useRef, useEffect, useState } from 'react';
import { Send, Loader2, AlertCircle } from 'lucide-react';
import useChat from '../store/chat';
import MessageBubble from './MessageBubble';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ChatWindow() {
  const {
    messages,
    isLoading,
    error,
    sessionId,
    addMessage,
    setLoading,
    setError,
  } = useChat();

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message
    addMessage({
      id: `msg_${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    });

    setLoading(true);
    setError(null);

    try {
      // Stream response
      const response = await fetch(
        `${API_BASE}/stream?message=${encodeURIComponent(userMessage)}&session_id=${sessionId}`,
        {
          method: 'GET',
          headers: {
            'Accept': 'text/event-stream',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      let fullContent = '';
      const decoder = new TextDecoder();
      let assistantMessageId = `msg_${Date.now()}`;
      let messageAdded = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              const chunk = data.chunk || '';
              fullContent += chunk;

              // Add assistant message on first chunk
              if (!messageAdded) {
                addMessage({
                  id: assistantMessageId,
                  role: 'assistant',
                  content: chunk,
                  timestamp: new Date().toISOString(),
                });
                messageAdded = true;
              } else {
                // Update last message with new content
                // This would require updating the store
              }
            } catch (e) {
              // Ignore parse errors
            }
          }
        }
      }

      setLoading(false);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      setLoading(false);
    }

    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-full bg-[#08080f]">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="mb-4 text-5xl">🤖</div>
            <h2 className="text-2xl font-bold text-white mb-2">Welcome to n8n Chatbot</h2>
            <p className="text-white/60 max-w-md">
              Start by asking me about finding leads, optimizing content, or any other task.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-white/60">
            <Loader2 size={16} className="animate-spin" />
            <span className="text-sm">Thinking...</span>
          </div>
        )}

        {error && (
          <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-red-400 text-sm font-medium">Error</p>
              <p className="text-red-300 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-white/5 bg-[#08080f]/80 backdrop-blur">
        <form onSubmit={handleSend} className="flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything... (e.g., 'Find me B2B SaaS leads')"
            disabled={isLoading}
            className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-indigo-500/50 focus:bg-white/10 transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium flex items-center gap-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Send size={18} />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </div>
  );
}