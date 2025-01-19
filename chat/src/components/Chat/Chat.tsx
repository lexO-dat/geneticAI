import React, { useState } from 'react';
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
    selectedUcf,
    setSelectedUcf,
    ucfOptions,
  } = useChatLogic();

  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const cleanFileName = (fileName: string) => {
    return fileName.replace(/^temp_[a-f0-9]{32}_/, '');
  };

  const handleFileClick = (file: string) => {
    setSelectedFile(file);
    setIsDrawerOpen(true);
  };

  const closeDrawer = () => {
    setIsDrawerOpen(false);
    setSelectedFile(null);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-96 bg-gray-800 text-white p-4 flex flex-col">
        <div className="mb-4">
          <h2 className="text-lg font-semibold mb-2">UCF Selection</h2>
          <select 
            value={selectedUcf}
            onChange={(e) => setSelectedUcf(Number(e.target.value))}
            className="w-full p-2 rounded bg-gray-700 text-white border border-gray-600"
          >
            {ucfOptions.map(ucf => (
              <option key={ucf.id} value={ucf.id}>
                {ucf.name}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-grow overflow-y-auto">
          <h2 className="text-lg font-semibold mb-2">Files</h2>
          {outputFiles.length > 0 ? (
            outputFiles.map((file) => (
              <div
                key={file}
                className="flex items-center space-x-2 py-2 px-2 hover:bg-gray-700 rounded cursor-pointer"
                onClick={() => handleFileClick(file)}
              >
                <File className="w-7 h-7" />
                <span>{cleanFileName(file)}</span>
              </div>
            ))
          ) : (
            <div className="text-gray-400">No files generated.</div>
          )}
        </div>
      </div>

      <div className="flex flex-col w-full bg-gray-100">
        <MessageList ref={chatContainerRef} messages={messages} isLoading={isLoading} />
        <MessageInput
          inputValue={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onSend={sendMessage}
        />
      </div>

      <div
        className={`
          fixed top-0 right-0 h-screen w-full sm:w-3/4 md:w-2/3 lg:w-2/3 xl:w-2/3
           text-white transform transition-transform duration-300
          ${isDrawerOpen ? 'translate-x-0' : 'translate-x-full'}
        `}
        style={{ zIndex: 9999 }}
      >
        {isDrawerOpen && (
          <div
            className="absolute top-0 left-0 w-screen h-screen text-white text bg-black bg-opacity-60"
            style={{ zIndex: -1 }}
            onClick={closeDrawer}
          />
        )}

        <div className="flex flex-col h-full">
          <div className="flex justify-end p-4 border-b">
            <button
              onClick={closeDrawer}
              className="py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded"
            >
              Close
            </button>
          </div>

          <div className="flex-grow overflow-auto p-4">
            <h2 className="text-xl font-bold mb-4">
              Preview: {selectedFile && cleanFileName(selectedFile)}
            </h2>

            {selectedFile ? (
              <div className="border text-white border-gray-500 p-2 rounded">
                <iframe
                  src={`http://localhost:8000/v1/outputs/${folderName}/${selectedFile}`}
                  title="preview"
                  className="w-full h-96 text-white"
                />
              </div>
            ) : (
              <p>There is no file selected</p>
            )}
          </div>

          {selectedFile && (
            <div className="p-4 text-white border-t flex justify-end">
              <a
                href={`http://localhost:8000/v1/outputs/${folderName}/${selectedFile}`}
                download
                target="_blank"
                rel="noopener noreferrer"
                className="py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded"
              >
                Download
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Chat;