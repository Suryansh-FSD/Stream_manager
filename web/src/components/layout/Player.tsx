"use client";

import React from "react";
import Link from "next/link";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Shuffle,
  Repeat,
  Repeat1,
  Volume2,
  VolumeX,
  Volume1,
  Heart,
  BarChart3,
} from "lucide-react";
import { useAudio } from "@/components/player/AudioContext";
import { formatDuration } from "@/lib/utils/format";

export function Player() {
  const {
    currentTrack,
    isPlaying,
    progress,
    duration,
    volume,
    isMuted,
    shuffle,
    repeat,
    isUsingSynth,
    togglePlay,
    seek,
    setVolume,
    toggleMute,
    nextTrack,
    prevTrack,
    toggleShuffle,
    cycleRepeat,
    toggleLike,
    isLiked,
  } = useAudio();

  if (!currentTrack) {
    return (
      <div className="h-20 bg-surface border-t border-white/5 px-4 flex items-center justify-between text-muted text-xs select-none">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded bg-surface-elevated flex items-center justify-center text-white/20">
            ♫
          </div>
          <div>
            <div className="text-white/60 font-medium">No track playing</div>
            <div className="text-muted-dark">Select any track to start listening</div>
          </div>
        </div>
        <div className="text-center text-white/40 hidden md:block">
          Spotify Trends Audio Player • Procedural synthesizer demonstration engine
        </div>
        <div className="flex items-center gap-2 text-white/40">
          <Volume2 className="w-4 h-4" />
          <div className="w-24 h-1 bg-white/10 rounded-full" />
        </div>
      </div>
    );
  }

  const progressPercent = duration > 0 ? (progress / duration) * 100 : 0;
  const liked = isLiked(currentTrack.id);

  return (
    <footer className="h-20 bg-surface border-t border-white/10 px-4 md:px-6 flex items-center justify-between text-white select-none z-50 fixed bottom-0 left-0 right-0">
      {/* Left: Track Info & Like */}
      <div className="flex items-center gap-3 w-1/4 min-w-[180px] max-w-[300px]">
        {currentTrack.cover_image_url ? (
          <img
            src={currentTrack.cover_image_url}
            alt={currentTrack.title}
            className="w-12 h-12 rounded object-cover shadow-md flex-shrink-0"
          />
        ) : (
          <div className="w-12 h-12 rounded bg-surface-elevated flex items-center justify-center text-sm font-bold flex-shrink-0">
            ♫
          </div>
        )}
        <div className="overflow-hidden mr-2">
          <Link
            href={`/track/${currentTrack.id}`}
            className="text-sm font-medium text-white hover:underline truncate block"
            title={currentTrack.title}
          >
            {currentTrack.title}
          </Link>
          <Link
            href={currentTrack.artist_id ? `/artist/${currentTrack.artist_id}` : "#"}
            className="text-xs text-muted hover:text-white hover:underline truncate block"
            title={currentTrack.artist_name}
          >
            {currentTrack.artist_name || "Unknown Artist"}
          </Link>
          <span className="text-[9px] uppercase tracking-wider px-1 py-0.2 rounded bg-white/10 text-emerald-400 font-mono inline-block">
            {isUsingSynth ? "Procedural Synth Demo" : "Audio Preview"}
          </span>
        </div>
        <button
          onClick={() => toggleLike(currentTrack)}
          className={`p-1 transition-colors ${
            liked ? "text-primary hover:text-primary-hover" : "text-muted hover:text-white"
          }`}
          title={liked ? "Remove from Liked Songs" : "Save to Liked Songs"}
        >
          <Heart className={`w-4 h-4 ${liked ? "fill-current" : ""}`} />
        </button>
      </div>

      {/* Center: Controls & Scrubber */}
      <div className="flex flex-col items-center justify-center max-w-[680px] w-2/4">
        <div className="flex items-center gap-4 mb-1">
          <button
            onClick={toggleShuffle}
            className={`p-1 text-sm transition-colors relative ${
              shuffle ? "text-primary" : "text-muted hover:text-white"
            }`}
            title="Toggle Shuffle"
          >
            <Shuffle className="w-4 h-4" />
            {shuffle && <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full" />}
          </button>

          <button
            onClick={prevTrack}
            className="text-muted hover:text-white transition-colors p-1"
            title="Previous track"
          >
            <SkipBack className="w-4 h-4" />
          </button>

          <button
            onClick={togglePlay}
            className="w-8 h-8 rounded-full bg-white hover:scale-105 active:scale-95 text-black flex items-center justify-center shadow-lg transition-transform"
            title={isPlaying ? "Pause" : "Play"}
          >
            {isPlaying ? (
              <Pause className="w-4 h-4 fill-current" />
            ) : (
              <Play className="w-4 h-4 fill-current ml-0.5" />
            )}
          </button>

          <button
            onClick={nextTrack}
            className="text-muted hover:text-white transition-colors p-1"
            title="Next track"
          >
            <SkipForward className="w-4 h-4" />
          </button>

          <button
            onClick={cycleRepeat}
            className={`p-1 text-sm transition-colors relative ${
              repeat !== "off" ? "text-primary" : "text-muted hover:text-white"
            }`}
            title={`Repeat: ${repeat}`}
          >
            {repeat === "one" ? <Repeat1 className="w-4 h-4" /> : <Repeat className="w-4 h-4" />}
            {repeat !== "off" && (
              <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full" />
            )}
          </button>
        </div>

        {/* Scrubber row */}
        <div className="w-full flex items-center gap-2 text-[11px] text-muted font-mono">
          <span className="w-9 text-right">{formatDuration(progress * 1000)}</span>
          <div className="relative flex-1 flex items-center group py-1">
            <input
              type="range"
              min={0}
              max={duration || 30}
              step={0.5}
              value={progress}
              onChange={(e) => seek(parseFloat(e.target.value))}
              className="w-full h-1 bg-white/20 rounded-lg appearance-none cursor-pointer group-hover:bg-white/30"
              style={{
                background: `linear-gradient(to right, #1DB954 ${progressPercent}%, rgba(255,255,255,0.2) ${progressPercent}%)`,
              }}
            />
          </div>
          <span className="w-9">{formatDuration(duration * 1000)}</span>
        </div>
      </div>

      {/* Right: Audio Features & Volume */}
      <div className="flex items-center justify-end gap-3 w-1/4 min-w-[180px] max-w-[280px]">
        <Link
          href={`/track/${currentTrack.id}`}
          className="p-1.5 text-muted hover:text-white transition-colors rounded hover:bg-white/5"
          title="Inspect Audio Features & Analytics"
        >
          <BarChart3 className="w-4 h-4" />
        </Link>

        <button
          onClick={toggleMute}
          className="text-muted hover:text-white transition-colors p-1"
          title={isMuted ? "Unmute" : "Mute"}
        >
          {isMuted || volume === 0 ? (
            <VolumeX className="w-4 h-4 text-red-400" />
          ) : volume < 0.5 ? (
            <Volume1 className="w-4 h-4" />
          ) : (
            <Volume2 className="w-4 h-4" />
          )}
        </button>

        <div className="w-24 group relative flex items-center py-1">
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={isMuted ? 0 : volume}
            onChange={(e) => setVolume(parseFloat(e.target.value))}
            className="w-full h-1 bg-white/20 rounded-lg appearance-none cursor-pointer group-hover:bg-white/30"
            style={{
              background: `linear-gradient(to right, #ffffff ${
                (isMuted ? 0 : volume) * 100
              }%, rgba(255,255,255,0.2) ${(isMuted ? 0 : volume) * 100}%)`,
            }}
          />
        </div>
      </div>
    </footer>
  );
}
