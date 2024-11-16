import React from 'react';

const LoadingIndicator: React.FC = () => {
  return (
    <div className="flex mb-4 justify-start">
      <div className="max-w-[70%] rounded-lg px-4 py-2 bg-zinc-800 text-zinc-100">
        <div className="flex space-x-1">
          <div className="h-2 w-2 bg-zinc-100 rounded-full animate-loading" style={{ animationDelay: '0s' }}></div>
          <div className="h-2 w-2 bg-zinc-100 rounded-full animate-loading" style={{ animationDelay: '0.2s' }}></div>
          <div className="h-2 w-2 bg-zinc-100 rounded-full animate-loading" style={{ animationDelay: '0.4s' }}></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;