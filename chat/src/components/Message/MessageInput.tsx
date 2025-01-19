import React from 'react';

interface MessageInputProps {
  inputValue: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSend: () => void;
}

const MessageInput: React.FC<MessageInputProps> = ({ inputValue, onChange, onSend }) => (
  <div className="p-4 bg-white">
    <div className="flex space-x-2">
      <input
        type="text"
        value={inputValue}
        onChange={onChange}
        onKeyPress={(e) => e.key === 'Enter' && onSend()}
        className="flex-1 p-2 border border-gray-300 rounded"
        placeholder="Escribe un mensaje..."
      />
      <button
        onClick={onSend}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Send
      </button>
    </div>
  </div>
);

export default MessageInput;
