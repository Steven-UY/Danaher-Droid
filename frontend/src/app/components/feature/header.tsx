import React from 'react';
import { Avatar, AvatarImage, AvatarFallback } from "../ui/avatar";

interface HeaderProps {
  avatarSrc: string;
  avatarAlt: string;
  title: string;
  subtitle: string;
}

const Header: React.FC<HeaderProps> = ({ avatarSrc, avatarAlt, title, subtitle }) => {
  return (
    <div className="p-4 border-zinc-800">
      <div className="flex flex-col items-center space-y-2">
        <Avatar className="w-20 h-20">
          <AvatarImage src={avatarSrc} alt={avatarAlt} />
          <AvatarFallback>IR</AvatarFallback>
        </Avatar>
        <h2 className="text-2xl font-bold">{title}</h2>
        <p className="text-zinc-400">{subtitle}</p>
      </div>
    </div>
  );
};

export default Header;