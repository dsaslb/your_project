import * as React from "react";

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Avatar({ className = "", ...props }: AvatarProps) {
  return (
    <div className={`inline-flex items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700 ${className}`} {...props} />
  );
}

export interface AvatarImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {}

export function AvatarImage({ className = "", ...props }: AvatarImageProps) {
  return <img className={`rounded-full object-cover ${className}`} {...props} />;
}

export interface AvatarFallbackProps extends React.HTMLAttributes<HTMLDivElement> {}

export function AvatarFallback({ className = "", ...props }: AvatarFallbackProps) {
  return (
    <div className={`rounded-full bg-gray-400 text-white flex items-center justify-center ${className}`} {...props} />
  );
} 