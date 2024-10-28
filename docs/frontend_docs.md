# Frontend Documentation

## Overview
This document will cover the technical details concering the frontend, which basically includes anything within the Next.js project. Also a quick summary (it's not everything) but the 

---

### Chatbot Interface

```typescript
import { useState, useRef, useEffect } from 'react'
```
- This line imports three React hooks. These hooks are core to how functional components in React manage state, side effects, and references. Here's an explanation of each one:
1. useState
 - Allows you to add state to your functional components. 
 2. useRef
 - Provides a way to persist values across renders without causing a re-render when the value changes
 3. useEffect
 - Lets you perform **side effects** in functional components e.g data fetching, DOM manipulation, timers, subscriptions. In the component it allows me to send requests to the Flask API.
 - Structure of a useEffect hook:
 ```typescript
 useEffect(() => {
  // Effect code (side effect) goes here

  return () => {
    // Cleanup code (optional)
  }
}, [dependencies]);
```

---

```typescript
import axios from 'axios'
```

- Axios is a JavaScript library used for making HTTP requests from either a **browser** or **Node.js** environment.
This allows applications to communicate with the backend server. Axios is used in my code through the following way:

```typescript
const response = await axios.post('http://127.0.0.1:5000/chat', 
  { message: input },  // Message payload sent in the request body
  { 
    headers: { 'Content-Type': 'application/json' } // Setting the content type
  }
)
```

- Here the ```axios.post``` sends data to the backend at ```http://127.0.0.1:5000/chat```.
- Along with the message payload and the specified headers

```typescript
type Message = {
  content: string;
  sender: 'user' | 'bot';
}
```

- The Messages type is used here to define the structure of each chat message

### State Management

#### 1. State Declaration

```typescript
const [messages, setMessages] = useState<Message[]>([
  { content: "Hello! How can I assist you today?", sender: 'bot' }
])
const [input, setInput] = useState('')
```

- We create a state variable **messages** here that holds an array of message objects(which we created type for) 
- We also created a state variable **input** that holds the current input text typed by the user

#### 2. Updating the Message State

- For context this function manages the process of sending a user's message and then receiving a bot response. 
- The ```setMessages``` function is called within ```handleSend``` to add both the user's and bot's messages to
the ```messages``` array. 

```typescript
const handleSend = async () => {
  if (input.trim()) {
    const userMessage: Message = { content: input, sender: 'user' }
    setMessages(prev => [...prev, userMessage])  // Adding user's message to messages
    setInput('')// Clears the input field automatically 

    try {
      const response = await axios.post('http://127.0.0.1:5000/chat', 
        { message: input },
        { headers: { 'Content-Type': 'application/json' } }
      )
      const botMessage: Message = { content: response.data.response, sender: 'bot' }
      setMessages(prev => [...prev, botMessage])  // Adding bot's message to messages
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = { content: 'Sorry, there was an error processing your message.', sender: 'bot' }
      setMessages(prev => [...prev, errorMessage])  // Adding error message to messages
    }
  }
}
```

- After a user sends a message it is appended to messages using the ```setMessages``` function
- Once the bot's response is received it is also appended to ```messages``` similarly the same is the case
for when an error is encountered.      

### Scrolling Behaviour

- The scrolling Behaviour ensures that the latest messages are automatically scrolled interview when a message is added

```typescript
const scrollAreaRef = useRef<HTMLDivElement>(null)

useEffect(() => {
  if (scrollAreaRef.current) {
    scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
  }
}, [messages])
```

- ```useRef<HTMLDivElement>(null)``` is a **React Hook** that creates a **reference** to a DOM element, which is the div 
element in this case. The reference allows you to directly access and manipulate the DOM elements without triggering a re-render. We 
assign the reference to ```scrollAreaRef```
- The ```useEffect``` hook is

```typescript
if (scrollAreaRef.current) {
  scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
}
```

- ```scrollAreaRef.current``` checks if the reference is attached to an element(i.e it exists)
- ```scrollAreaRef.current.scrollTop``` to ```scrollHeight``` scrolls the chat area to the very bottom,
which makes the message visible
- ```scrollAreaRef.current.scrollHeight``` gives the total height of the scrollable content

### Entering Messages into Input Field

- The function ```handleKeyDown``` allows the user to press the Enter key and have the user send the message 
based on what is sent in the input.      

```typescript
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }
```

- The parameter ```(e: React.KeyboardEvent<HTMLTextAreaElement>)```
 - The function takes a keyboard event (e) of type ```React.KeyboardEvent<HTMLTextAreaElement>```
 - This type is specific to keyboard events on a ```<textarea>``` element, allowing TypeScript to provide relevant autocomplete and error checking. 

```typescript
if (e.key === 'Enter' && !e.shiftKey) 
```

- This checks if the key pressed is Enter and that shift is not being pressed
- Which means that the function only completes when Enter is pressed alone

### Functional Component Return Statement

This part of the code is what actually renders the chat interface. It has two main sections:
a scrollable area displaying the messages and an input area for sending any new messages. Here
is a detailed breakdown:

#### Chat Display Area

```typescript
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
```






























































