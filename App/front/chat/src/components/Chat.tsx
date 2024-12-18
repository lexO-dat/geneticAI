import React, { useState, useEffect, useRef } from 'react';

interface Message {
  text: string;
  isUser: boolean;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (inputMessage.trim() === '') return;

    const newUserMessage: Message = { text: inputMessage, isUser: true };
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setInputMessage('');
    setIsLoading(true);

    let verilogCode = '';

    try {
      // Enviar mensaje al generador de Verilog
      const generateResponse = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: "custom-llama-v1", prompt: inputMessage }),
      });

      if (!generateResponse.ok) throw new Error('Error al obtener el código Verilog.');

      // Leer respuesta en streaming
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

      if (!verilogCode.trim()) throw new Error('No se obtuvo código Verilog.');

      // Enviar código Verilog a /run_cello
      const celloResponse = await fetch('http://localhost:8000/run_cello', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          verilog_code: verilogCode,
          ucf_index: 1,
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

      // Construir la URL del archivo PDF
      if (celloData.folder_name) {
        // Ajustar el nombre del PDF según corresponda a tu entorno
        const pdfUrl = `http://localhost:8000/outputs/${celloData.folder_name}/${celloData.folder_name}_Eco1C1G1T1.UCF._dpl-sbol.pdf`;
        console.log('Abriendo PDF en una nueva pestaña:', pdfUrl);
        window.open(pdfUrl, '_blank'); // Abre el PDF en una pestaña nueva
      }

      // Convertir message y result a string si son objetos
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

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-xs p-3 rounded-lg ${
                message.isUser ? 'bg-blue-500 text-white' : 'bg-gray-300 text-black'
              }`}
              style={{ whiteSpace: 'pre-wrap' }}
            >
              {message.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-xs p-3 rounded-lg bg-gray-300 text-black animate-pulse">...</div>
          </div>
        )}
      </div>
      <div className="p-4 bg-white">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            className="flex-1 p-2 border border-gray-300 rounded"
            placeholder="Escribe un mensaje..."
          />
          <button
            onClick={sendMessage}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
