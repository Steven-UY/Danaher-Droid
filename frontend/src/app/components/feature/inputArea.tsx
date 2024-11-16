import React from 'react';
import { Button } from "../ui/button";
import { Send, Phone } from 'lucide-react';
import { Textarea } from "../ui/textarea";

interface InputAreaProps {
  input: string;
  onInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
  onStartStopRecording: () => void;
  isRecording: boolean;
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
}

const InputArea: React.FC<InputAreaProps> = ({
  input,
  onInputChange,
  onSend,
  onStartStopRecording,
  isRecording,
  onKeyDown
}) => {
  return (
    <div className="flex items-center space-x-2">
      <Textarea
        placeholder="Ask John Danaher a question..."
        value={input}
        onChange={onInputChange}
        onKeyDown={onKeyDown}
        className="flex-grow bg-zinc-800 text-zinc-100 border-none focus:ring-0"
        rows={1}
      />
      <Button onClick={onSend} size="icon" className="bg-zinc-700 hover:bg-zinc-600">
        <Send className="h-4 w-4" />
        <span className="sr-only">Send</span>
      </Button>
      <Button 
        onClick={onStartStopRecording}
        className={`${isRecording ? 'bg-red-500' : 'bg-zinc-700'} hover:bg-zinc-600`}
        size="icon"
      >
        <Phone className="h-4 w-4" />
        <span className="sr-only">
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </span>
      </Button>
    </div>
  );
};

export default InputArea;