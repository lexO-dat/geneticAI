import { useEffect } from 'react';
import { useChatState } from './useChatState';
import { ucfOptions } from '../constants/ucfOptions';
import { fetchVerilogCode, fetchUcfFile, fetchCelloProcessing } from '../api/api';

export const useChatLogic = () => {
  const {
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
  } = useChatState();

  const sendMessage = async () => {
    if (inputMessage.trim() === '') return;
  
    setMessages(prev => [...prev, { text: inputMessage, isUser: true }]);
    setInputMessage('');
    setIsLoading(true);
  
    try {
      setMessages(prev => [...prev, { text: 'Generating Verilog code...', isUser: false }]);
  
      const verilogCode = await fetchVerilogCode(inputMessage);
  
      setMessages(prev => [...prev, { text: 'Generated Verilog Code:', isUser: false }]);
      setMessages(prev => [...prev, { text: verilogCode, isUser: false }]);
      setMessages(prev => [...prev, { text: 'Selecting UCF file based on your prompt', isUser: false }]);

  
      const ucfName = await fetchUcfFile(inputMessage);
      if (!ucfName) {
        setMessages(prev => [...prev, { text: 'No UCF file found based on your prompt, selecting the default one (Eco1C1G1T1).', isUser: false }]);
      }

      const selectedUcfOption = ucfOptions.find(ucf => ucf.name === ucfName);
      if (!selectedUcfOption) throw new Error(`UCF "${ucfName}" not found in options.`);
  
      setMessages(prev => [...prev, { text: `Selected UCF: ${ucfName}`, isUser: false }]);
  
      setMessages(prev => [...prev, { text: 'Processing with Cello...', isUser: false }]);

      const celloResult = await fetchCelloProcessing(verilogCode, selectedUcfOption.id);
      if (celloResult.output_files) setOutputFiles(celloResult.output_files);
      if (celloResult.folder_name) setFolderName(celloResult.folder_name);
  
      setMessages(prev => [...prev, { text: 'Cello processing completed.', isUser: false }]);
  
    } catch (error: any) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { text: `Error: ${error.message}`, isUser: false }]);
    } finally {
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  return {
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
  };
};
