export type Message = {
    content: string;
    sender: 'user' | 'bot';
  };
  
  export interface CustomMediaRecorder extends MediaRecorder {
    ondataavailable: (event: BlobEvent) => void;
    onstop: () => void;
  }