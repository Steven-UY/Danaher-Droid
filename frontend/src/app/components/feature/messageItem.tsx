import React from 'react';

type Sender = 'user' | 'bot';

interface MessageItemProps {
  message: {
    content: string;
    sender: Sender;
  };
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  return (
    <div className={`flex mb-4 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          message.sender === 'user' ? 'bg-zinc-700 text-zinc-100' : 'bg-zinc-800 text-zinc-100'
        }`}
      >
        {message.content}
      </div>
    </div>
  );
};

export default MessageItem;