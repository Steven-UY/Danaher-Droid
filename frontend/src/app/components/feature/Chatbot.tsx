"use client";

import { useState, useRef, useLayoutEffect, useEffect } from 'react';
import { Send, Phone } from 'lucide-react';
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { ScrollArea } from "../ui/scroll-area";
import { Avatar, AvatarImage, AvatarFallback } from "../ui/avatar";
import axios from 'axios';

type Message = {
  content: string;
  sender: 'user' | 'bot';
};

interface CustomMediaRecorder extends MediaRecorder {
  start: () => void;
  stop: () => void;
  ondataavailable: (event: BlobEvent) => void;
  onstop: () => void;
}


export const useRecordVoice = () => {
  
};


export default function ChatbotInterface() {
  const [messages, setMessages] = useState<Message[]>([
    { content: "You’re on the mats with John Danaher after class...", sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [displayedMessage, setDisplayedMessage] = useState<string>('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(false); // For loading animation
  const [isTyping, setIsTyping] = useState(false); // For typing effect
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [mediaRecorder, setMediaRecorder] = useState<CustomMediaRecorder | null>(null);
  const [recording, setRecording] = useState(false);
  const chunks = useRef<Blob[]>([]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then((stream) => {
          const recorder = new MediaRecorder(stream);
          
          recorder.ondataavailable = (e: BlobEvent) => {
            chunks.current.push(e.data);
          };
          
          recorder.onstop = async () => {
            const audioBlob = new Blob(chunks.current, { type: 'audio/wav' });
            chunks.current = [];
            // Handle the audio blob - convert to text later
            console.log('Recording stopped, blob created:', audioBlob);
          };
          
          setMediaRecorder(recorder as CustomMediaRecorder);
        })
        .catch(console.error);
    }
  }, []);


  const startRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'inactive') {
      chunks.current = []; // Clear previous chunks
      mediaRecorder.start();
      setRecording(true);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      (mediaRecorder as CustomMediaRecorder).stop();
      setRecording(false);
    }
  };

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

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage: Message = { content: input, sender: 'user' };
      setMessages((prev) => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);

      try {
        const response = await axios.post(
          'http://127.0.0.1:5000/chat',
          { 
            message: input,
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
    setDisplayedMessage(''); // Clear displayed message before typing effect starts
    setIsTyping(true); // Start typing effect

    const typingInterval = setInterval(() => {
      if (index < text.length) {
        setDisplayedMessage((prev) => prev + text[index]);
        index++;
      } else {
        clearInterval(typingInterval);
        // After typing effect is done, add the full message to messages
        const botMessage: Message = { content: text, sender: 'bot' };
        setMessages((prev) => [...prev, botMessage]);
        setDisplayedMessage(''); // Clear displayedMessage
        setIsTyping(false); // Stop typing effect
      }
    }, 5); // Adjust typing speed by changing the interval time
  };

  useEffect(() => {
    const scrollContainer = scrollAreaRef.current?.querySelector(
      '[data-radix-scroll-area-viewport]'
    );
  
    if (scrollContainer) {
      const handleScroll = () => {
        const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
        const isUserAtBottom = scrollTop + clientHeight >= scrollHeight - 10; // Threshold of 10px
        setIsAtBottom(isUserAtBottom);
      };
  
      scrollContainer.addEventListener('scroll', handleScroll);
  
      // Cleanup the event listener
      return () => {
        scrollContainer.removeEventListener('scroll', handleScroll);
      };
    }
  }, []);
  

  return (
    <div className="flex flex-col h-screen w-screen items-center bg-zinc-900 text-zinc-100 overflow-x-hidden">
      <div className="max-w-2xl w-full mx-auto flex flex-col h-full bg-zinc-900">
        <div className="p-4 border-zinc-800">
          <div className="flex flex-col items-center space-y-2">
            <Avatar className="w-20 h-20">
              <AvatarImage src="/assets/danaher.jpg" alt="John Danaher" />
              <AvatarFallback>IR</AvatarFallback>
            </Avatar>
            <h2 className="text-2xl font-bold">John Danaher</h2>
            <p className="text-zinc-400">Only Wears Rashguards.</p>
          </div>
        </div>
        <ScrollArea ref={scrollAreaRef} className="flex-1 px-4 py-0 overflow-x-hidden">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex mb-4 ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[70%] rounded-lg px-4 py-2 ${
                  message.sender === 'user'
                    ? 'bg-zinc-700 text-zinc-100'
                    : 'bg-zinc-800 text-zinc-100'
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}

          {/* Loading Animation */}
          {isLoading && (
            <div className="flex mb-4 justify-start">
              <div className="max-w-[70%] rounded-lg px-4 py-2 bg-zinc-800 text-zinc-100">
                <div className="flex space-x-1">
                  <div
                    className="h-2 w-2 bg-zinc-100 rounded-full animate-loading"
                    style={{ animationDelay: '0s' }}
                  ></div>
                  <div
                    className="h-2 w-2 bg-zinc-100 rounded-full animate-loading"
                    style={{ animationDelay: '0.2s' }}
                  ></div>
                  <div
                    className="h-2 w-2 bg-zinc-100 rounded-full animate-loading"
                    style={{ animationDelay: '0.4s' }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          {/* Typing Effect */}
          {isTyping && displayedMessage && (
            <div className="flex mb-4 justify-start">
              <div className="max-w-[70%] rounded-lg px-4 py-2 bg-zinc-800 text-zinc-100">
                {displayedMessage}
              </div>
            </div>
          )}
        </ScrollArea>
        <div className="border-zinc-800 p-4">
          <div className="flex items-center space-x-2">
            <Textarea
              placeholder="Ask John Danaher a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-grow bg-zinc-800 text-zinc-100 border-none focus:ring-0"
              rows={1}
            />
            <Button onClick={handleSend} size="icon" className="bg-zinc-700 hover:bg-zinc-600">
              <Send className="h-4 w-4" />
              <span className="sr-only">Send</span>
            </Button>
            <Button 
            onClick={recording ? stopRecording : startRecording}
            className={`${recording ? 'bg-red-500' : 'bg-zinc-700'} hover:bg-zinc-600`}
            >
            <Phone className="h-4 w-4" />
            <span className="sr-only">
            {recording ? 'Stop Recording' : 'Start Recording'}
            </span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
