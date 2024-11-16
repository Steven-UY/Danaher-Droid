import React from 'react';
import MessageItem from './messageItem';

interface Message {
  content: string;
  sender: 'user' | 'bot';
}

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <>
      {messages.map((message, index) => (
        <MessageItem key={index} message={message} />
      ))}
    </>
  );
};

export default MessageList;