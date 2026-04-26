import React from 'react';
import type { Message } from '../store/chat';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-slide-in`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-indigo-600 text-white'
            : 'bg-white/10 border border-white/20 text-white/90'
        }`}
      >
        <p className="text-sm leading-relaxed break-words">{message.content}</p>
        {message.workflow && !isUser && (
          <div className="mt-2 pt-2 border-t border-white/10">
            <div className="flex items-center justify-between text-xs text-white/60">
              <span className="font-mono">{message.workflow}</span>
              {message.confidence && (
                <span className="ml-2 text-indigo-300">{message.confidence}</span>
              )}
            </div>
          </div>
        )}
        <span className="text-xs text-white/40 mt-2 block">
          {new Date(message.timestamp).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
}