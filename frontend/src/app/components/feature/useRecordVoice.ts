import { useState, useEffect, useRef } from 'react';

interface CustomMediaRecorder extends MediaRecorder { //How is MediaRecorder being instantiated?
  ondataavailable: (event: BlobEvent) => void;
  onstop: () => void;
}

export const useRecordVoice = (onAudioRecorded: (blob: Blob) => void) => {
  const [audioRecorder, setAudioRecorder] = useState<CustomMediaRecorder | null>(null);
  const [recording, setRecording] = useState(false);
  const chunks = useRef<Blob[]>([]);

  //Event handlers
  const handleDataAvailable = (e: BlobEvent) => {
    chunks.current.push(e.data);
  };

  //When the audio recording stops, the blob is created and the onAudioRecorded function is called
  const handleRecordingStop = () => {
    const audioBlob = new Blob(chunks.current, { type: 'audio/mp3' });
    chunks.current = [];
    console.log('Recording stopped, blob created:', audioBlob);

    onAudioRecorded(audioBlob);
  };

  useEffect(() => {
    if (typeof window === "undefined") return;

    const initializeRecorder = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
      
        recorder.ondataavailable = handleDataAvailable;
        recorder.onstop = handleRecordingStop; //.onstop part of API activates when .stop called
      
        setAudioRecorder(recorder as CustomMediaRecorder);
      } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Please enable microphone access to use voice input features.');
      }
    };
  
    initializeRecorder();


    return () => {
      if (audioRecorder) {
        audioRecorder.stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [audioRecorder]);

  //user triggered functions
  const startRecording = () => {
    if (audioRecorder && audioRecorder.state === 'inactive') {
      chunks.current = [];
      audioRecorder.start();
      setRecording(true);
    }
  };

  const stopRecording = () => {
    if (audioRecorder) {
      audioRecorder.stop();
      setRecording(false);
    }
  };
  
  return { recording, startRecording, stopRecording };
};