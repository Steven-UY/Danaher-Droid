import React from 'react';

interface TypingEffectProps {
  displayedMessage: string;
}

const TypingEffect: React.FC<TypingEffectProps> = ({ displayedMessage }) => {
  return (
    <div className="flex mb-4 justify-start">
      <div className="max-w-[70%] rounded-lg px-4 py-2 bg-zinc-800 text-zinc-100">
        {displayedMessage}
      </div>
    </div>
  );
};

export default TypingEffect;