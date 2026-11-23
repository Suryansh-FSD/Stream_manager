"use client";

import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { Track } from "@/lib/data/types";
import { audioSynth } from "@/lib/audio-synth";

interface AudioContextType {
  currentTrack: Track | null;
  isPlaying: boolean;
  progress: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  queue: Track[];
  history: Track[];
  shuffle: boolean;
  repeat: "off" | "all" | "one";
  isUsingSynth: boolean;
  likedTrackIds: Set<string>;
  playTrack: (track: Track, newQueue?: Track[]) => void;
  pause: () => void;
  resume: () => void;
  togglePlay: () => void;
  seek: (seconds: number) => void;
  setVolume: (vol: number) => void;
  toggleMute: () => void;
  nextTrack: () => void;
  prevTrack: () => void;
  toggleShuffle: () => void;
  cycleRepeat: () => void;
  toggleLike: (track: Track) => void;
  isLiked: (trackId: string) => boolean;
}

const AudioContext = createContext<AudioContextType | undefined>(undefined);

export function AudioProvider({ children }: { children: React.ReactNode }) {
  const [currentTrack, setCurrentTrack] = useState<Track | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [duration, setDuration] = useState<number>(30); // 30s preview default
  const [volume, setVolumeState] = useState<number>(0.8);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [queue, setQueue] = useState<Track[]>([]);
  const [history, setHistory] = useState<Track[]>([]);
  const [shuffle, setShuffle] = useState<boolean>(false);
  const [repeat, setRepeat] = useState<"off" | "all" | "one">("off");
  const [isUsingSynth, setIsUsingSynth] = useState<boolean>(true);
  const [likedTrackIds, setLikedTrackIds] = useState<Set<string>>(new Set());

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const progressTimerRef = useRef<any>(null);
  const isUsingSynthRef = useRef<boolean>(false);

  // Initialize saved liked tracks from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem("spotify_trends_likes");
      if (saved) {
        const ids = JSON.parse(saved);
        setLikedTrackIds(new Set(ids));
      }
    } catch {
      // Ignore localStorage access restrictions
    }
  }, []);

  const toggleLike = (track: Track) => {
    setLikedTrackIds((prev) => {
      const next = new Set(prev);
      if (next.has(track.id)) {
        next.delete(track.id);
      } else {
        next.add(track.id);
      }
      try {
        localStorage.setItem("spotify_trends_likes", JSON.stringify(Array.from(next)));
      } catch {}
      return next;
    });
  };

  const isLiked = (trackId: string) => likedTrackIds.has(trackId);

  // Clean timer on unmount
  useEffect(() => {
    return () => {
      if (progressTimerRef.current) clearInterval(progressTimerRef.current);
      audioSynth.stop();
    };
  }, []);

  const startProgressTimer = (maxDuration: number) => {
    if (progressTimerRef.current) clearInterval(progressTimerRef.current);
    progressTimerRef.current = setInterval(() => {
      setProgress((prev) => {
        if (prev >= maxDuration) {
          handleTrackEnded();
          return 0;
        }
        return prev + 0.5;
      });
    }, 500);
  };

  const handleTrackEnded = () => {
    if (repeat === "one" && currentTrack) {
      seek(0);
      playTrack(currentTrack);
    } else {
      nextTrack();
    }
  };

  const playTrack = (track: Track, newQueue?: Track[]) => {
    if (currentTrack?.id !== track.id) {
      if (currentTrack) {
        setHistory((h) => [currentTrack, ...h.slice(0, 20)]);
      }
      setCurrentTrack(track);
    }

    if (newQueue && newQueue.length > 0) {
      setQueue(newQueue);
    }

    setProgress(0);
    const trackDuration = track.duration_ms ? Math.round(track.duration_ms / 1000) : 30;
    setDuration(trackDuration);

    // If track has a valid preview url
    if (track.preview_url && track.preview_url.startsWith("http")) {
      isUsingSynthRef.current = false;
      setIsUsingSynth(false);
      audioSynth.stop();
      if (!audioRef.current) {
        audioRef.current = new Audio();
        audioRef.current.onended = handleTrackEnded;
      }
      audioRef.current.src = track.preview_url;
      audioRef.current.volume = isMuted ? 0 : volume;
      audioRef.current.play().catch(() => {
        // Fall back to synth if audio fails
        isUsingSynthRef.current = true;
        setIsUsingSynth(true);
        audioSynth.play(track);
      });
    } else {
      // Use Web Audio API synthesizer for instant preview
      isUsingSynthRef.current = true;
      setIsUsingSynth(true);
      if (audioRef.current) {
        audioRef.current.pause();
      }
      audioSynth.setVolume(isMuted ? 0 : volume);
      audioSynth.play(track);
    }

    setIsPlaying(true);
    startProgressTimer(trackDuration);
  };

  const pause = () => {
    setIsPlaying(false);
    if (progressTimerRef.current) clearInterval(progressTimerRef.current);
    if (isUsingSynthRef.current) {
      audioSynth.stop();
    } else if (audioRef.current) {
      audioRef.current.pause();
    }
  };

  const resume = () => {
    if (!currentTrack) return;
    setIsPlaying(true);
    if (isUsingSynthRef.current) {
      audioSynth.play(currentTrack);
    } else if (audioRef.current) {
      audioRef.current.play().catch(() => {});
    }
    startProgressTimer(duration);
  };

  const togglePlay = () => {
    if (isPlaying) {
      pause();
    } else {
      if (currentTrack) {
        resume();
      }
    }
  };

  const seek = (seconds: number) => {
    const validSec = Math.max(0, Math.min(duration, seconds));
    setProgress(validSec);
    if (!isUsingSynthRef.current && audioRef.current) {
      audioRef.current.currentTime = validSec;
    }
  };

  const setVolume = (vol: number) => {
    const clamped = Math.max(0, Math.min(1, vol));
    setVolumeState(clamped);
    setIsMuted(clamped === 0);
    audioSynth.setVolume(clamped);
    if (audioRef.current) {
      audioRef.current.volume = clamped;
    }
  };

  const toggleMute = () => {
    if (isMuted) {
      setIsMuted(false);
      audioSynth.setVolume(volume || 0.8);
      if (audioRef.current) audioRef.current.volume = volume || 0.8;
    } else {
      setIsMuted(true);
      audioSynth.setVolume(0);
      if (audioRef.current) audioRef.current.volume = 0;
    }
  };

  const nextTrack = () => {
    if (queue.length === 0) {
      pause();
      return;
    }
    let nextIdx = 0;
    if (shuffle) {
      nextIdx = Math.floor(Math.random() * queue.length);
    }
    const nextItem = queue[nextIdx];
    const newQueue = queue.filter((_, idx) => idx !== nextIdx);
    setQueue(newQueue);
    playTrack(nextItem);
  };

  const prevTrack = () => {
    if (progress > 3) {
      seek(0);
      return;
    }
    if (history.length > 0) {
      const prevItem = history[0];
      setHistory((h) => h.slice(1));
      if (currentTrack) {
        setQueue((q) => [currentTrack, ...q]);
      }
      playTrack(prevItem);
    } else {
      seek(0);
    }
  };

  const toggleShuffle = () => setShuffle((s) => !s);

  const cycleRepeat = () => {
    setRepeat((r) => (r === "off" ? "all" : r === "all" ? "one" : "off"));
  };

  return (
    <AudioContext.Provider
      value={{
        currentTrack,
        isPlaying,
        progress,
        duration,
        volume,
        isMuted,
        queue,
        history,
        shuffle,
        repeat,
        isUsingSynth,
        likedTrackIds,
        playTrack,
        pause,
        resume,
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
      }}
    >
      {children}
    </AudioContext.Provider>
  );
}

export function useAudio() {
  const context = useContext(AudioContext);
  if (!context) {
    throw new Error("useAudio must be used within an AudioProvider");
  }
  return context;
}
