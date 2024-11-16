"use client";

import React, { useState, useRef, useEffect, useLayoutEffect } from 'react';
import Header from './header';
import MessageList from './messageList';
import LoadingIndicator from './loadingIndicator';
import TypingEffect from './typingEffect';
import InputArea from './inputArea';
import { ScrollArea } from "../ui/scroll-area";
import axios from 'axios';
import { Message } from './types';
import { useRecordVoice } from './useRecordVoice';

const ChatbotInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { content: "You’re on the mats with John Danaher after class...", sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [displayedMessage, setDisplayedMessage] = useState<string>('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isAtBottom, setIsAtBottom] = useState(true);

  // Voice recording state and functions from custom hook
  const { recording, startRecording, stopRecording } = useRecordVoice();

  const scrollToBottom = () => {
    if (isAtBottom && scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector(
        '[data-radix-scroll-area-viewport]'
      );
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  };

  useLayoutEffect(() => {
    scrollToBottom();
  }, [messages, displayedMessage]);

  useEffect(() => {
    const scrollContainer = scrollAreaRef.current?.querySelector(
      '[data-radix-scroll-area-viewport]'
    );
  
    if (scrollContainer) {
      const handleScroll = () => {
        const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
        const isUserAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
        setIsAtBottom(isUserAtBottom);
      };
  
      scrollContainer.addEventListener('scroll', handleScroll);
  
      return () => {
        scrollContainer.removeEventListener('scroll', handleScroll);
      };
    }
  }, []);

  const handleSend = async (messageInput?: string) => {
    const message = messageInput || input;
    if (message.trim()) {
      const userMessage: Message = { content: message, sender: 'user' };
      setMessages((prev) => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);

      try {
        const response = await axios.post(
          'http://127.0.0.1:5000/chat',
          { 
            message: message,
          },
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );
        setIsLoading(false);
        simulateTypingEffect(response.data.response);
      } catch (error) {
        console.error('Error sending message:', error);
        const errorMessage: Message = {
          content: 'Sorry, there was an error processing your message.',
          sender: 'bot',
        };
        setMessages((prev) => [...prev, errorMessage]);
        setIsLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const simulateTypingEffect = (text: string) => {
    let index = 0;
    setDisplayedMessage('');
    setIsTyping(true);

    const typingInterval = setInterval(() => {
      if (index < text.length) {
        setDisplayedMessage((prev) => prev + text[index]);
        index++;
      } else {
        clearInterval(typingInterval);
        const botMessage: Message = { content: text, sender: 'bot' };
        setMessages((prev) => [...prev, botMessage]);
        setDisplayedMessage('');
        setIsTyping(false);
      }
    }, 5); // Adjust typing speed by changing the interval time
  };

  return (
    <div className="flex flex-col h-screen w-screen items-center bg-zinc-900 text-zinc-100 overflow-x-hidden">
      <div className="max-w-2xl w-full mx-auto flex flex-col h-full bg-zinc-900">
        <Header 
          avatarSrc="/assets/danaher.jpg" 
          avatarAlt="John Danaher" 
          title="John Danaher" 
          subtitle="Only Wears Rashguards." 
        />
        <ScrollArea ref={scrollAreaRef} className="flex-1 px-4 py-0 overflow-x-hidden">
          <MessageList messages={messages} />
          
          {/* Loading Animation */}
          {isLoading && <LoadingIndicator />}

          {/* Typing Effect */}
          {isTyping && displayedMessage && <TypingEffect displayedMessage={displayedMessage} />}
        </ScrollArea>
        <div className="border-zinc-800 p-4">
          <InputArea 
            input={input}
            onInputChange={(e) => setInput(e.target.value)}
            onSend={() => handleSend()}
            onStartStopRecording={recording ? stopRecording : startRecording}
            isRecording={recording}
            onKeyDown={handleKeyDown}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatbotInterface;

