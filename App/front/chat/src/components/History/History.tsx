// History.tsx
import React, { useEffect, useState } from 'react';
import { MessageSquareIcon, TrashIcon } from 'lucide-react';

interface Chat {
  id: number;
  messages: { text: string; sender: string; timestamp: string }[];
}

interface HistoryProps {
  onSelectChat: (chatId: number) => void;
  onDeleteChat: (chatId: number) => void;
  chats: Chat[];  // Recibimos la lista de chats como prop
}

const History: React.FC<HistoryProps> = ({ onSelectChat, onDeleteChat, chats }) => {
  return (
    <div className="flex flex-col space-y-2">
      {chats.map((chat) => (
        <div
          key={chat.id}
          className="flex items-center justify-between space-x-2 py-2 px-2 hover:bg-gray-700 rounded cursor-pointer"
        >
          {/* Al hacer clic en un chat, lo seleccionamos */}
          <div className="flex items-center space-x-2" onClick={() => onSelectChat(chat.id)}>
            <MessageSquareIcon className="w-5 h-5" />
            <span>{`Chat ${chat.id}`}</span>
          </div>
          {/* Al hacer clic en el icono de basura, eliminamos el chat */}
          <button
            onClick={() => onDeleteChat(chat.id)}
            className="text-red-500 hover:text-red-700"
          >
            <TrashIcon className="w-5 h-5" />
          </button>
        </div>
      ))}
    </div>
  );
};

export default History;
