"use client";

import React from "react";
import Link from "next/link";
import { Play } from "lucide-react";

interface CardProps {
  title: string;
  subtitle?: string;
  imageUrl?: string | null;
  href: string;
  type?: "album" | "artist" | "genre" | "track";
  onPlay?: () => void;
  badge?: string;
}

export function Card({
  title,
  subtitle,
  imageUrl,
  href,
  type = "album",
  onPlay,
  badge,
}: CardProps) {
  const isArtist = type === "artist";

  return (
    <div className="group relative p-3.5 rounded-lg bg-surface hover:bg-surface-elevated transition-all duration-200 flex flex-col select-none">
      {/* Artwork container */}
      <div className="relative w-full aspect-square mb-3.5 overflow-hidden shadow-md">
        <Link href={href} className="block w-full h-full">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={title}
              className={`w-full h-full object-cover transition-transform duration-300 group-hover:scale-105 ${
                isArtist ? "rounded-full" : "rounded-md"
              }`}
            />
          ) : (
            <div
              className={`w-full h-full bg-surface-highlight flex items-center justify-center text-white/30 text-2xl font-bold ${
                isArtist ? "rounded-full" : "rounded-md"
              }`}
            >
              {title.charAt(0)}
            </div>
          )}
        </Link>

        {badge && (
          <span className="absolute top-2 left-2 text-[10px] font-bold px-1.5 py-0.5 rounded bg-black/70 text-primary border border-primary/30 backdrop-blur-sm">
            {badge}
          </span>
        )}

        {/* Floating Play Button */}
        {onPlay && (
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onPlay();
            }}
            className="absolute bottom-2 right-2 w-11 h-11 rounded-full bg-primary hover:bg-primary-hover active:scale-95 text-black flex items-center justify-center shadow-xl opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-200 z-10"
            title={`Play ${title}`}
          >
            <Play className="w-5 h-5 fill-black ml-0.5" />
          </button>
        )}
      </div>

      {/* Info */}
      <div className="flex flex-col min-w-0">
        <Link
          href={href}
          className="font-semibold text-sm text-white hover:underline truncate block"
          title={title}
        >
          {title}
        </Link>
        {subtitle && (
          <p className="text-xs text-muted truncate mt-0.5" title={subtitle}>
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}
