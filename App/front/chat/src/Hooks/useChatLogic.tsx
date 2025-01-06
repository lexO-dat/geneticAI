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
      { text: 'Generating verilog code...', isUser: false }
    ]);

    try {
      // Llamada a la API de Ollama para generar código Verilog
      const generateResponse = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: "custom-llama-v1", prompt: inputMessage }),
      });

      if (!generateResponse.ok) throw new Error('Error obtaining the verilog code, try sending again the message.');

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

      if (!verilogCode.trim()) throw new Error('Error, try sending again the message.');
      
      /* verilogCode = `
      module top (
      input A,
      input B,
      output reg [3:0] AtC_out,
      output reg Xyle_out, 
      output reg RFP_out,
      output reg YFP_out
    );
    
    wire Xor;
    assign Xor = (~A & ~B);
    
    wire XYLE_in = Xor;
    assign XYLE_in = Xor;
    module and_gate (
        input Xyle_in,
        input xylose_in,
        output AND_output
      );
       always @(Xyle_in, xylose_in)
          begin
            if(Xyle_in == 1 && xylose_in == 1) 
              AND_output = 1'b1;
            else 
              AND_output = 1'b0;
           end
      endmodule;
    
    module AtC (
       input Xor,
       output reg [3:0] AtC_out
     );
       always @(Xor)
         begin
          if(Xor == 1) AtC_out <= 4'd2;
          else AtC_out <= 4'd0;
        end
      endmodule;
    
    module RFP (
        input Xor,
        output reg RFP_out
      );
      always @(Xor)
       begin
           if(Xor == 1) RFP_out <= 4'd1; 
          else RFP_out <= 4'd0;
       end1. Executing Verilog-2005 frontend: /home/lexo/Desktop/Practica/App/library/verilogs/temp_34f66ec566d444f2bbe34683ddf5e902.v
Parsing Verilog input from `/home/lexo/Desktop/Practica/App/library/verilogs/temp_34f66ec566d444f2bbe34683ddf5e902.v' to AST representation.
/home/lexo/Desktop/Practica/App/library/verilogs/temp_34f66ec566d444f2bbe34683ddf5e902.v:7: ERROR: Illegal integer constant size of zero (IEEE 1800-2012, 5.7).
    endmodule;
    
    module YFP (
        input Xor,
        output reg YFP_out
      );
      always @(Xor)
       begin
           if(Xor == 1) YFP_out <= 4'd3; 
          else YFP_out <= 4'd0;
       end
    endmodule;
    
    assign AtC_out = AtC.Xor;
    assign Xyle_out = AND_output;
    assign RFP_out = RFP.Xor;
    assign YFP_out = YFP.Xor;

  endmodule` */

      setMessages(prevMessages => [
        ...prevMessages,
        { text: 'Generated verilog:', isUser: false },
        { text: verilogCode, isUser: false },
        { text: 'Processing the verilog with cello..', isUser: false }
      ]);

      // LLamada a la API de Cello para procesar el código Verilog y generar el circuito genético
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

      if (!celloResponse.ok) throw new Error('Error processing the verilog file.');
      const celloData = await celloResponse.json();
      //console.log('Respuesta de /run_cello:', celloData);

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

      /* const celloResult =
        typeof celloData.result === 'object'
          ? JSON.stringify(celloData.result, null, 2)
          : celloData.result || 'Proceso completado sin detalles adicionales.'; */

      setMessages(prevMessages => [
        ...prevMessages,
        { text: celloMessage, isUser: false },

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

