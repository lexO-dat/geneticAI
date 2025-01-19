import React from "react";

interface MessageProps {
    text: string;
    isUser: boolean;
}

const Message: React.FC<MessageProps> = ({ text, isUser }) => (    
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
        <div
            className={`max-w-xs p-3 rounded-lg ${
            isUser ? 'bg-blue-500 text-white' : 'bg-gray-300 text-black'
            }`}
            style={{ whiteSpace: 'pre-wrap' }}
        >
            {text}
        </div>
    </div>
);

export default Message;