"use client";

import React from "react";
import Link from "next/link";
import {
  Play,
  Pause,
  Heart,
  BarChart3,
  Calendar,
  Clock,
  Sparkles,
  ExternalLink,
  Volume2,
} from "lucide-react";
import { TrackDetail } from "@/lib/data/types";
import { useAudio } from "@/components/player/AudioContext";
import { AudioFeatureRadar } from "@/components/ui/AudioFeatureRadar";
import { formatDuration, formatStreams, formatNumber, formatDate } from "@/lib/utils/format";
import { getGradientForId } from "@/lib/utils/colors";

const PITCH_CLASSES = [
  "C",
  "C♯ / D♭",
  "D",
  "D♯ / E♭",
  "E",
  "F",
  "F♯ / G♭",
  "G",
  "G♯ / A♭",
  "A",
  "A♯ / B♭",
  "B",
];

interface TrackClientProps {
  track: TrackDetail;
}

export function TrackClient({ track }: TrackClientProps) {
  const { currentTrack, isPlaying, playTrack, togglePlay, isLiked, toggleLike } =
    useAudio();

  const isCurrent = currentTrack?.id === track.id;
  const isThisPlaying = isCurrent && isPlaying;
  const liked = isLiked(track.id);
  const gradient = getGradientForId(track.id);
  const feat = track.audio_features;

  const keyName = feat ? PITCH_CLASSES[feat.key % 12] : "Unknown";
  const modeName = feat ? (feat.mode === 1 ? "Major" : "Minor") : "";

  const handlePlay = () => {
    if (isCurrent) {
      togglePlay();
    } else {
      playTrack(track);
    }
  };

  const featureBars = feat
    ? [
        {
          name: "Danceability",
          value: feat.danceability,
          desc: "How suitable a track is for dancing based on tempo, rhythm stability, beat strength.",
        },
        {
          name: "Energy",
          value: feat.energy,
          desc: "Perceptual measure of intensity, dynamic range, and activity.",
        },
        {
          name: "Valence (Musical Positiveness)",
          value: feat.valence,
          desc: "Tracks with high valence sound more positive, happy, and euphoric.",
        },
        {
          name: "Acousticness",
          value: feat.acousticness,
          desc: "Confidence measure of acoustic vs synthetic instrumentation.",
        },
        {
          name: "Instrumentalness",
          value: feat.instrumentalness,
          desc: "Predicts whether a track contains no spoken or sung vocals.",
        },
        {
          name: "Liveness",
          value: feat.liveness,
          desc: "Detects the presence of an audience in the recording.",
        },
        {
          name: "Speechiness",
          value: feat.speechiness,
          desc: "Detects the presence of spoken words (rap, speech, audio).",
        },
      ]
    : [];

  return (
    <div className="space-y-8 select-none">
      {/* Hero Header */}
      <div
        className={`p-8 md:p-10 pt-16 bg-gradient-to-b ${gradient} flex flex-col md:flex-row md:items-end gap-6 shadow-inner`}
      >
        <img
          src={track.cover_image_url || "/placeholder-album.png"}
          alt={track.title}
          className="w-48 h-48 md:w-56 md:h-56 rounded-lg object-cover shadow-2xl flex-shrink-0 ring-1 ring-white/10"
        />
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase font-bold tracking-wider text-white/80">
              Song
            </span>
            {track.explicit && (
              <span className="text-[10px] font-bold bg-white/20 text-white px-1.5 py-0.5 rounded uppercase">
                Explicit
              </span>
            )}
          </div>
          <h1 className="text-3xl md:text-5xl font-black text-white tracking-tight">
            {track.title}
          </h1>
          <div className="flex flex-wrap items-center gap-2 text-xs sm:text-sm text-white/90">
            {track.artist_id ? (
              <Link
                href={`/artist/${track.artist_id}`}
                className="font-bold text-white hover:underline"
              >
                {track.artist_name || "Unknown Artist"}
              </Link>
            ) : (
              <span className="font-bold text-white">{track.artist_name || "Unknown Artist"}</span>
            )}
            <span>•</span>
            {track.album_id ? (
              <Link
                href={`/album/${track.album_id}`}
                className="hover:underline text-white/90"
              >
                {track.album_title || "Single"}
              </Link>
            ) : (
              <span>{track.album_title || "Single"}</span>
            )}
            <span>•</span>
            <span>{formatDuration(track.duration_ms)}</span>
          </div>
        </div>
      </div>

      <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
        {/* Play Action Bar */}
        <div className="flex items-center gap-4">
          <button
            onClick={handlePlay}
            className="w-14 h-14 rounded-full bg-primary hover:bg-primary-hover active:scale-95 text-black flex items-center justify-center shadow-xl transition-all"
            title={isThisPlaying ? "Pause" : "Play"}
          >
            {isThisPlaying ? (
              <Pause className="w-6 h-6 fill-black" />
            ) : (
              <Play className="w-6 h-6 fill-black ml-0.5" />
            )}
          </button>

          <button
            onClick={() => toggleLike(track)}
            className={`p-3 rounded-full hover:bg-white/10 transition-colors ${
              liked ? "text-primary" : "text-muted hover:text-white"
            }`}
            title={liked ? "Remove from Liked Songs" : "Save to Liked Songs"}
          >
            <Heart className={`w-6 h-6 ${liked ? "fill-current" : ""}`} />
          </button>

          <Link
            href="/analytics"
            className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-surface-elevated hover:bg-surface-highlight border border-white/10 text-white text-xs font-semibold"
          >
            <BarChart3 className="w-4 h-4 text-primary" />
            <span>Open in Streamlit Studio</span>
          </Link>
        </div>

        {/* Core Metrics Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-surface border border-white/5 space-y-1">
            <span className="text-xs text-muted">Synthetic Benchmark Streams</span>
            <div className="text-xl font-bold font-mono text-white">
              {formatStreams(track.streams)}
            </div>
            <div className="text-[11px] text-muted-dark font-mono">
              {formatNumber(track.streams)} (Demo Dataset)
            </div>
          </div>

          <div className="p-4 rounded-xl bg-surface border border-white/5 space-y-1">
            <span className="text-xs text-muted">Popularity Score</span>
            <div className="text-xl font-bold font-mono text-emerald-400">
              {track.popularity || 0} / 100
            </div>
            <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full"
                style={{ width: `${track.popularity || 0}%` }}
              />
            </div>
          </div>

          <div className="p-4 rounded-xl bg-surface border border-white/5 space-y-1">
            <span className="text-xs text-muted">Key & Scale</span>
            <div className="text-xl font-bold text-white">
              {keyName} {modeName}
            </div>
            <div className="text-[11px] text-muted-dark">
              {feat ? `${feat.time_signature}/4 Time Signature` : "Standard"}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-surface border border-white/5 space-y-1">
            <span className="text-xs text-muted">Tempo & Loudness</span>
            <div className="text-xl font-bold font-mono text-white">
              {feat ? `${Math.round(feat.tempo)} BPM` : "--"}
            </div>
            <div className="text-[11px] text-muted-dark font-mono">
              {feat ? `${feat.loudness.toFixed(1)} dB` : "--"}
            </div>
          </div>
        </div>

        {/* Audio Intelligence Section: Radar & Bars */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Radar Visualizer */}
          <div className="p-6 rounded-2xl bg-surface border border-white/5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">Audio Fingerprint</h3>
                <p className="text-xs text-muted">Radar profile across 7 audio dimensions</p>
              </div>
              <Sparkles className="w-5 h-5 text-primary" />
            </div>
            <AudioFeatureRadar features={feat} />
          </div>

          {/* Feature Breakdown Progress Bars */}
          <div className="p-6 rounded-2xl bg-surface border border-white/5 space-y-4">
            <div>
              <h3 className="text-lg font-bold text-white">Acoustic Attributes</h3>
              <p className="text-xs text-muted">Normalized values extracted by pipeline</p>
            </div>

            <div className="space-y-3.5 pt-2">
              {featureBars.map((item) => {
                const percent = Math.round(item.value * 100);
                return (
                  <div key={item.name} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-white">{item.name}</span>
                      <span className="font-mono text-muted">{percent}%</span>
                    </div>
                    <div className="w-full bg-surface-elevated h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-primary h-full rounded-full transition-all duration-500"
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                    <p className="text-[10px] text-muted-dark leading-tight">{item.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
