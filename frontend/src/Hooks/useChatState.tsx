import { useState, useRef } from 'react';

export interface Message {
  text: string;
  isUser: boolean;
}

export const useChatState = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [outputFiles, setOutputFiles] = useState<string[]>([]);
  const [folderName, setFolderName] = useState<string>('');
  const [selectedUcf, setSelectedUcf] = useState<number>(1);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  return {
    messages,
    setMessages,
    inputMessage,
    setInputMessage,
    isLoading,
    setIsLoading,
    outputFiles,
    setOutputFiles,
    folderName,
    setFolderName,
    selectedUcf,
    setSelectedUcf,
    chatContainerRef,
  };
};
