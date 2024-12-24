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
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (inputMessage.trim() === '') return;

    const newUserMessage: Message = { text: inputMessage, isUser: true };
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setInputMessage('');
    setIsLoading(true);

    let verilogCode = '';

    setMessages(prevMessages => [
      ...prevMessages,
      { text: 'Generando código Verilog...', isUser: false }
    ]);

    try {
      // Llamada a la API de Ollama para generar código Verilog
      const generateResponse = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: "custom-llama-v1", prompt: inputMessage }),
      });

      if (!generateResponse.ok) throw new Error('Error al obtener el código Verilog.');

      const reader = generateResponse.body?.getReader();
      if (!reader) throw new Error('No se pudo leer la respuesta.');

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
              console.error('Error al parsear JSON:', error);
            }
          }
          boundary = buffer.indexOf('\n');
        }

        ({ value: chunk, done: readerDone } = await reader.read());
      }

      if (!verilogCode.trim()) throw new Error('Error, intenta enviar el mensaje nuevamente.');

      setMessages(prevMessages => [
        ...prevMessages,
        { text: 'Código Verilog generado:', isUser: false },
        { text: verilogCode, isUser: false },
        { text: 'Procesando código con Cello...', isUser: false }
      ]);

      // LLamada a la API de Cello para procesar el código Verilog y generar el circuito genético
      const celloResponse = await fetch('http://localhost:8000/run_cello', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          verilog_code: verilogCode,
          ucf_index: 4,
          options: {
            verbose: true,
            log_overwrite: false,
            print_iters: false,
            exhaustive: false,
            test_configs: false,
          },
        }),
      });

      if (!celloResponse.ok) throw new Error('Error al procesar el código con Cello.');
      const celloData = await celloResponse.json();
      console.log('Respuesta de /run_cello:', celloData);

      if (celloData.output_files) {
        setOutputFiles(celloData.output_files);
      }

      // Establecer el folder_name
      if (celloData.folder_name) {
        setFolderName(celloData.folder_name);
      }

      const celloMessage =
        typeof celloData.message === 'object'
          ? JSON.stringify(celloData.message, null, 2)
          : celloData.message || 'Proceso de Cello completado.';

      const celloResult =
        typeof celloData.result === 'object'
          ? JSON.stringify(celloData.result, null, 2)
          : celloData.result || 'Proceso completado sin detalles adicionales.';

      setMessages(prevMessages => [
        ...prevMessages,
        { text: celloMessage, isUser: false },
        { text: celloResult, isUser: false }
      ]);

    } catch (error: any) {
      console.error('Error:', error);
      const errorMessage: Message = { text: `Error: ${error.message}`, isUser: false };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
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
  };
};

