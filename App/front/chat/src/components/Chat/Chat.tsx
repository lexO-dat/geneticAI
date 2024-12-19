// Chat.tsx
import React, { useState } from 'react';
import MessageList from '../Message/MessageList';
import MessageInput from '../Message/MessageInput';
import { useChatLogic } from '../../Hooks/useChatLogic';
import History from '../History/History'; // Importa el componente History
import { PlusIcon, TrashIcon } from 'lucide-react';

const Chat: React.FC = () => {
  const {
    messages,
    setMessages,
    inputMessage,
    setInputMessage,
    isLoading,
    sendMessage,
    loadChat,
    deleteChat,
    chats,  // Recibimos la lista de chats
    chatContainerRef,
    createNewChat, // Llamamos a createNewChat desde el hook
  } = useChatLogic();

  const handleCreateNewChat = () => {
    if (messages.length === 0) {
      // Si los mensajes están vacíos, creamos un nuevo chat
      createNewChat();
    } else {
      // Si ya hay mensajes, actualizamos el chat existente
      createNewChat();
    }
  };

  const handleDeleteChat = (chatId: number) => {
    deleteChat(chatId);
    setMessages([]); // Limpiar los mensajes al eliminar un chat
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-80 bg-gray-800 text-white p-4 flex flex-col">
        <button
          onClick={handleCreateNewChat} // Crear o actualizar el chat
          className="flex items-center justify-center space-x-2 bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded mb-4"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Nuevo chat</span>
        </button>

        {/* Chat History */}
        <div className="flex-grow overflow-y-auto">
          <h2 className="text-lg font-semibold mb-2">Historial de chats</h2>
          <History
            chats={chats} // Pasamos los chats cargados
            onSelectChat={(chatId) => loadChat(chatId)}
            onDeleteChat={handleDeleteChat}
          />
        </div>
      </div>

      {/* Main content area */}
      <div className="flex flex-col w-full bg-gray-100">
        <MessageList ref={chatContainerRef} messages={messages} isLoading={isLoading} />
        <MessageInput
          inputValue={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onSend={sendMessage}
        />
      </div>
    </div>
  );
};

export default Chat;
