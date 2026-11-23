"use client";

import React from "react";
import Link from "next/link";
import { Play, Pause, Heart, Sparkles } from "lucide-react";
import { Track } from "@/lib/data/types";
import { useAudio } from "@/components/player/AudioContext";
import { formatDuration, formatStreams } from "@/lib/utils/format";

interface TrackRowProps {
  track: Track;
  index: number;
  playlistQueue?: Track[];
  showAlbum?: boolean;
  showCover?: boolean;
}

export function TrackRow({
  track,
  index,
  playlistQueue,
  showAlbum = true,
  showCover = true,
}: TrackRowProps) {
  const { currentTrack, isPlaying, playTrack, togglePlay, isLiked, toggleLike } =
    useAudio();

  const isCurrent = currentTrack?.id === track.id;
  const isThisPlaying = isCurrent && isPlaying;
  const liked = isLiked(track.id);

  const handlePlayClick = () => {
    if (isCurrent) {
      togglePlay();
    } else {
      playTrack(track, playlistQueue);
    }
  };

  return (
    <div
      className={`group flex items-center px-4 py-2.5 rounded-md hover:bg-surface-elevated text-sm transition-colors select-none ${
        isCurrent ? "bg-white/5" : ""
      }`}
    >
      {/* Index or Play icon */}
      <div className="w-8 flex-shrink-0 flex items-center justify-center text-muted font-mono text-xs">
        <span className={`group-hover:hidden ${isCurrent ? "text-primary font-bold" : ""}`}>
          {isThisPlaying ? (
            <span className="flex items-center gap-0.5 h-3">
              <span className="w-1 h-3 bg-primary animate-pulse rounded-full" />
              <span className="w-1 h-2 bg-primary animate-pulse rounded-full delay-100" />
              <span className="w-1 h-3.5 bg-primary animate-pulse rounded-full delay-200" />
            </span>
          ) : (
            index + 1
          )}
        </span>
        <button
          onClick={handlePlayClick}
          className="hidden group-hover:flex items-center justify-center text-white hover:text-primary transition-colors"
          title={isThisPlaying ? "Pause" : "Play"}
        >
          {isThisPlaying ? (
            <Pause className="w-4 h-4 fill-current" />
          ) : (
            <Play className="w-4 h-4 fill-current ml-0.5" />
          )}
        </button>
      </div>

      {/* Track Title, Artist, & Optional Cover */}
      <div className="flex items-center gap-3 flex-1 min-w-0 pr-4">
        {showCover && (
          <img
            src={track.cover_image_url || "/placeholder-album.png"}
            alt={track.title}
            className="w-10 h-10 rounded object-cover flex-shrink-0 shadow-sm"
          />
        )}
        <div className="overflow-hidden">
          <div className="flex items-center gap-2">
            <Link
              href={`/track/${track.id}`}
              className={`font-medium truncate hover:underline ${
                isCurrent ? "text-primary font-semibold" : "text-white"
              }`}
              title={track.title}
            >
              {track.title}
            </Link>
            {track.explicit && (
              <span className="text-[10px] font-bold bg-white/20 text-white/80 px-1 py-0.2 rounded uppercase tracking-wider flex-shrink-0">
                E
              </span>
            )}
          </div>
          <div className="text-xs text-muted truncate mt-0.5">
            {track.artist_id ? (
              <Link
                href={`/artist/${track.artist_id}`}
                className="hover:text-white hover:underline"
              >
                {track.artist_name || "Unknown Artist"}
              </Link>
            ) : (
              <span>{track.artist_name || "Unknown Artist"}</span>
            )}
          </div>
        </div>
      </div>

      {/* Album (hidden on tablet/mobile) */}
      {showAlbum && (
        <div className="hidden md:block flex-1 min-w-0 pr-4 text-xs text-muted truncate">
          {track.album_id ? (
            <Link
              href={`/album/${track.album_id}`}
              className="hover:text-white hover:underline truncate block"
            >
              {track.album_title || "Single"}
            </Link>
          ) : (
            <span>{track.album_title || "Single"}</span>
          )}
        </div>
      )}

      {/* Popularity or Streams */}
      <div className="hidden lg:flex items-center justify-end w-32 pr-4 text-xs text-muted font-mono">
        {track.streams ? (
          <span>{formatStreams(track.streams)}</span>
        ) : (
          <span>Pop: {track.popularity || 0}</span>
        )}
      </div>

      {/* Like Button */}
      <div className="w-10 flex-shrink-0 flex items-center justify-center">
        <button
          onClick={() => toggleLike(track)}
          className={`p-1 transition-colors ${
            liked
              ? "text-primary hover:text-primary-hover"
              : "text-muted hover:text-white opacity-0 group-hover:opacity-100"
          }`}
          title={liked ? "Remove from Liked Songs" : "Save to Liked Songs"}
        >
          <Heart className={`w-4 h-4 ${liked ? "fill-current" : ""}`} />
        </button>
      </div>

      {/* Duration */}
      <div className="w-14 flex-shrink-0 text-right text-xs text-muted font-mono">
        {formatDuration(track.duration_ms)}
      </div>
    </div>
  );
}
