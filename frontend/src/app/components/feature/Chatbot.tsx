'use client'

import { useState, useRef, useLayoutEffect } from 'react'
import { Send } from 'lucide-react'
import { Button } from "../ui/button"
import { Textarea } from "../ui/textarea"
import { ScrollArea } from "../ui/scroll-area"
import axios from 'axios'  // Make sure to install axios: npm install axios

type Message = {
  content: string;
  sender: 'user' | 'bot';
}

export default function ChatbotInterface() {
  const [messages, setMessages] = useState<Message[]>([
    { content: "Hello! How can I assist you today?", sender: 'bot' }
  ])
  const [input, setInput] = useState('')
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }

  useLayoutEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (input.trim()) { //if input is empty the function exits early skipping entire block
      const userMessage: Message = { content: input, sender: 'user' }
      setMessages(prev => [...prev, userMessage])
      setInput('')

      try {
        const response = await axios.post('http://127.0.0.1:5000/chat', 
          { message: input },
          { 
            headers: {
              'Content-Type': 'application/json',
            }
          }
        )
        const botMessage: Message = { content: response.data.response, sender: 'bot' }
        setMessages(prev => [...prev, botMessage])
      } catch (error) {
        console.error('Error sending message:', error)
        const errorMessage: Message = { content: 'Sorry, there was an error processing your message.', sender: 'bot' }
        setMessages(prev => [...prev, errorMessage])
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  //represents the return statement of the functional component
  return (
    <div className="flex flex-col h-screen w-full bg-background">
      <div className="flex-1 overflow-hidden w-full">
        <ScrollArea ref={scrollAreaRef} className="h-full w-full p-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex w-full ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.sender === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
        </ScrollArea>
      </div>
      <div className="border-t bg-background p-4 w-full">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="flex items-end space-x-2 w-full"
        >
          <Textarea
            ref={textareaRef}
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-grow min-h-[60px] max-h-[200px] resize-none"
            rows={1}
          />
          <Button type="submit" size="icon" className="h-[60px] w-[60px]">
            <Send className="h-6 w-6" />
            <span className="sr-only">Send</span>
          </Button>
        </form>
      </div>
    </div>
  )
}
