import { useState, useRef, useEffect } from 'react';

interface Message {
  text: string;
  isUser: boolean;
}

export const useChatLogic = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [outputFiles, setOutputFiles] = useState<string[]>([]);
  const [folderName, setFolderName] = useState<string>('');
  const [selectedUcf, setSelectedUcf] = useState<number>(1);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const ucfOptions = [
    { id: 0, name: "Bth1C1G1T1" }, 
    { id: 1, name: "Eco1C1G1T1" },
    { id: 2, name: "Eco1C2G2T2" }, 
    { id: 3, name: "Eco2C1G3T1" }, 
    { id: 4, name: "Eco2C1G5T1" },
    { id: 5, name: "SC1C1G1T1" },
  ];

  const sendMessage = async () => {
    if (inputMessage.trim() === '') return;

    const newUserMessage: Message = { text: inputMessage, isUser: true };
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setInputMessage('');
    setIsLoading(true);

    let verilogCode = '';

    setMessages(prevMessages => [
      ...prevMessages,
      /* { text: 'Selected UCF: ' + ucfOptions.find(u => u.id === selectedUcf)?.name, isUser: false }, */
      { text: 'Generating verilog code...', isUser: false }
    ]);

    try {
      const generateResponse = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: "custom-llama-8b", prompt: inputMessage }),
      });

      if (!generateResponse.ok) throw new Error('Error obtaining the verilog code.');

      const reader = generateResponse.body?.getReader();
      if (!reader) throw new Error('Error reading the response body.');

      const decoder = new TextDecoder('utf-8');
      let { value: chunk, done: readerDone } = await reader.read();
      let buffer = '';

      while (!readerDone) {
        buffer += decoder.decode(chunk, { stream: true });
        let boundary = buffer.indexOf('\n');

        while (boundary !== -1) {
          const completeChunk = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 1);

          if (completeChunk.trim()) {
            try {
              const parsed = JSON.parse(completeChunk);
              if (parsed.response) verilogCode += parsed.response;
            } catch (error) {
              console.error('Error parsing the json:', error);
            }
          }
          boundary = buffer.indexOf('\n');
        }

        ({ value: chunk, done: readerDone } = await reader.read());
      }

      if (!verilogCode.trim()) throw new Error('No verilog code generated.');

      verilogCode = verilogCode.replace(/&&|\|\|/g, match => (match === '&&' ? '&' : '|'));

      const regex = /module\s+top[\s\S]*?endmodule/;
      let match = verilogCode.match(regex);

      console.log(match)

      if (match) {
        console.log(match[0]); // This will print the matched code block
      } else {
        console.log('No match found.');
      }

      if (!match) throw new Error('No module top found in the verilog code.');

      setMessages(prevMessages => [
        ...prevMessages,
        { text: 'Generated verilog:', isUser: false },
        { text: match[0], isUser: false },
        { text: 'Selecting a ucf file...', isUser: false }
      ]);

      while (!verilogCode) {}

      const ucfResponse = await fetch('http://localhost:8001/v1/rag/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: inputMessage })
      });

      if (!ucfResponse.ok) {
        throw new Error(`HTTP error! status: ${ucfResponse.status}`);
      }

      const responseData = await ucfResponse.json();

      const ucfName = responseData.answer.trim();
    
      const selectedUcf = ucfOptions.find(ucf => ucf.name === ucfName);
    
      if (!selectedUcf) {
        throw new Error(`UCF "${ucfName}" not found in options`);
      }
      

      setMessages(prevMessages => [
        ...prevMessages,
        {text: 'Selected ucf: ', isUser: false},
        {text: selectedUcf.name, isUser: false}
      ]);

      const celloResponse = await fetch('http://localhost:8000/v1/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          verilogCode: verilogCode,
          ucfIndex: selectedUcf.id,
          options: {
            verbose: true,
            log_overwrite: false,
            print_iters: false,
            exhaustive: false,
            test_configs: false,
          },
        }),
      });

      if (!celloResponse.ok) throw new Error('Cello processing failed.');
      const celloData = await celloResponse.json();

      if (celloData.output_files) setOutputFiles(celloData.output_files);
      if (celloData.folder_name) setFolderName(celloData.folder_name);

      const celloMessage = typeof celloData.message === 'object' 
        ? JSON.stringify(celloData.message, null, 2) 
        : celloData.message || 'Cello processing completed.';

      setMessages(prevMessages => [...prevMessages, { text: celloMessage, isUser: false }]);

    } catch (error: any) {
      console.error('Error:', error);
      setMessages(prevMessages => [...prevMessages, { text: `Error: ${error.message}`, isUser: false }]);
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
    setMessages,
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