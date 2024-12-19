import React, { forwardRef } from 'react';
import Message from "./Message";

interface MessageItem {
    text: string;
    isUser: boolean;
}

interface MessageListProps {
    messages: MessageItem[];
    isLoading: boolean;
}

const MessageList = forwardRef<HTMLDivElement, MessageListProps>(({ messages, isLoading }, ref) => {
    return (
      <div ref={ref} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <Message key={index} text={message.text} isUser={message.isUser} />
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-xs p-3 rounded-lg bg-gray-300 text-black animate-pulse">...</div>
          </div>
        )}
      </div>
    );
  });
  
  export default MessageList;
  