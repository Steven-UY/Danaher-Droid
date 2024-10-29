'use client'

import { useState, useRef, useLayoutEffect } from 'react'
import { Send, Phone} from 'lucide-react'
import { Button } from "../ui/button"
import { Textarea } from "../ui/textarea"
import { ScrollArea } from "../ui/scroll-area"
import { Avatar, AvatarImage, AvatarFallback } from "../ui/avatar" 
import axios from 'axios'  // Make sure to install axios: npm install axios

type Message = {
  content: string;
  sender: 'user' | 'bot';
}

export default function ChatbotInterface() {
  const [messages, setMessages] = useState<Message[]>([
    { content: "You’re on the mats with John Danaher after class, watching him replay a recent grappling match on his tablet. Kneeling beside him, he’s completely absorbed, eyes locked on the screen as he breaks down each move in silence. The quiet echoes of the video fill the gym, and you sit nearby, waiting, knowing he’ll share his insights once he’s ready to speak.", sender: 'bot' }
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
    if (input.trim()) {
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
  
  return (
    <div className="flex flex-col h-screen w-screen items-center bg-zinc-900 text-zinc-100 overflow-x-hidden">
      <div className="max-w-xl w-full mx-auto flex flex-col h-full bg-zinc-900">
        <div className="p-4 border-zinc-800">
          {/* Centered Avatar, Name, and Subtitle */}
          <div className="flex flex-col items-center space-y-2">
            <Avatar className="w-16 h-16">
              <AvatarImage src="/placeholder.svg?height=64&width=64" alt="John Danaher" />
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
                {message.content.split('\n').map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
            </div>
          ))}
        </ScrollArea>
        <div className="border-zinc-800 p-4">
          <div className="flex items-center space-x-2">
            <Textarea
              ref={textareaRef}
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
            <Button size="icon" className="bg-zinc-700 hover:bg-zinc-600">
              <Phone className="h-4 w-4" />
              <span className="sr-only">Call</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );  
}
