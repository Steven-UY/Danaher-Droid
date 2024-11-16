import { useState, useEffect, useRef } from 'react';

interface CustomMediaRecorder extends MediaRecorder {
  ondataavailable: (event: BlobEvent) => void;
  onstop: () => void;
}

export const useRecordVoice = () => {
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
            console.log('Recording stopped, blob created:', audioBlob);

            // TODO: Implement audio processing (e.g., send to backend)
          };
          
          setMediaRecorder(recorder as CustomMediaRecorder);
        })
        .catch((error) => {
          console.error('Error accessing microphone:', error);
          alert('Microphone access is required for voice input.');
        });
    }

    return () => {
      if (mediaRecorder) {
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [mediaRecorder]);

  const startRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'inactive') {
      chunks.current = [];
      mediaRecorder.start();
      setRecording(true);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setRecording(false);
    }
  };

  return { recording, startRecording, stopRecording };
};