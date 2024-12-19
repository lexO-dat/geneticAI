import { useState, useRef, useEffect } from 'react';

interface Message {
  text: string;
  isUser: boolean;
}

export const useChatLogic = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentChatId, setCurrentChatId] = useState<number | null>(null);  // Nuevo estado para almacenar el chat actual
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Función para enviar un mensaje
  const sendMessage = async () => {
    if (inputMessage.trim() === '') return;

    const newUserMessage: Message = { text: inputMessage, isUser: true };
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setInputMessage('');
    setIsLoading(true);

    let verilogCode = '';

    try {
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

      if (!verilogCode.trim()) throw new Error('No se obtuvo código Verilog.');

      const celloResponse = await fetch('http://localhost:8000/run_cello', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ verilog_code: verilogCode }),
      });

      if (!celloResponse.ok) throw new Error('Error al procesar el código con Cello.');
      const celloData = await celloResponse.json();

      if (celloData.folder_name) {
        const pdfUrl = `http://localhost:8000/outputs/${celloData.folder_name}/${celloData.folder_name}_Eco1C1G1T1.UCF._dpl-sbol.pdf`;
        window.open(pdfUrl, '_blank');
      }

      const celloMessage = celloData.message || 'Proceso de Cello completado.';
      const celloResult = celloData.result || 'Proceso completado sin detalles adicionales.';

      setMessages(prevMessages => [
        ...prevMessages,
        { text: celloMessage, isUser: false },
        { text: celloResult, isUser: false }
      ]);

      // Actualizar el chat en localStorage si ya existe
      if (currentChatId !== null) {
        updateChatInLocalStorage(currentChatId);
      }

    } catch (error: any) {
      console.error('Error:', error);
      const errorMessage: Message = { text: `Error: ${error.message}`, isUser: false };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Función para cargar un chat desde localStorage
  const loadChat = (chatId: number) => {
    const storedChat = localStorage.getItem(`chat-${chatId}`);
    if (storedChat) {
      const chat = JSON.parse(storedChat);
      setMessages(chat.messages);
      setCurrentChatId(chat.id); // Establecer el chat actual
    }
  };

  // Función para crear un nuevo chat
  const createNewChat = () => {
    if (messages.length > 0) {
      const chatId = new Date().getTime(); // Usar timestamp como ID único
      const newChat = {
        id: chatId,
        messages,
      };
      localStorage.setItem(`chat-${chatId}`, JSON.stringify(newChat));
      setCurrentChatId(chatId); // Establecer el chat actual
    }
  };

  // Función para actualizar un chat en localStorage
  const updateChatInLocalStorage = (chatId: number) => {
    const updatedChat = {
      id: chatId,
      messages,
    };
    localStorage.setItem(`chat-${chatId}`, JSON.stringify(updatedChat));
  };

  // Función para eliminar un chat de localStorage
  const deleteChat = (chatId: number) => {
    localStorage.removeItem(`chat-${chatId}`);
    setMessages([]); // Limpiar mensajes al eliminar el chat
    setCurrentChatId(null); // Restablecer el chat actual
  };

  // Función para cargar todos los chats desde localStorage
  const loadChats = () => {
    const storedChats: any[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('chat-')) {
        const chat = JSON.parse(localStorage.getItem(key)!);
        storedChats.push(chat);
      }
    }
    return storedChats;
  };

  useEffect(() => {
    if (currentChatId === null && messages.length === 0) {
      // Si no hay mensajes y no hay chat cargado, creamos un nuevo chat
      createNewChat();
    }
  }, [messages]);

  return {
    messages,
    setMessages,
    inputMessage,
    setInputMessage,
    isLoading,
    sendMessage,
    loadChat,
    deleteChat,
    loadChats,
    createNewChat,  // Asegúrate de exportar createNewChat aquí
    chats: loadChats(), // Cargar los chats desde localStorage
    chatContainerRef
  };
};
