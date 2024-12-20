import React from 'react';
import MessageList from '../Message/MessageList';
import MessageInput from '../Message/MessageInput';
import { useChatLogic } from '../../Hooks/useChatLogic';
import { File } from 'lucide-react';

const Chat: React.FC = () => {
  const {
    messages,
    inputMessage,
    setInputMessage,
    isLoading,
    sendMessage,
    chatContainerRef,
    outputFiles,
    folderName,
  } = useChatLogic();

  const cleanFileName = (fileName: string) => {
    return fileName.replace(/^temp_[a-f0-9]{32}_/, '');
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-96 bg-gray-800 text-white p-4 flex flex-col">
        {/* Apartado de archivos generados */}
        <div className="flex-grow overflow-y-auto">
          <h2 className="text-lg font-semibold mb-2">Archivos</h2>
          {/* Archivos generados dinámicamente */}
          {outputFiles.length > 0 ? (
            outputFiles.map((file) => (
              <div key={file} className="flex items-center space-x-2 py-2 px-2 hover:bg-gray-700 rounded cursor-pointer">
                <a
                  href={`http://localhost:8000/outputs/${folderName}/${file}`}
                  target="_blank"               
                  rel="noopener noreferrer"  
                  className="flex items-center space-x-2"
                >
                  <File className="w-7 h-7" />
                  <span>{cleanFileName(file)}</span>
                </a>
              </div>
            ))
          ) : (
            <div className="text-gray-400">No se han generado archivos aún.</div>
          )}
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
