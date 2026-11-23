"use client";

import React from "react";
import Link from "next/link";
import { Play, CheckCircle2, Heart, Music, BarChart3, Sparkles } from "lucide-react";
import { ArtistDetail, Track } from "@/lib/data/types";
import { useAudio } from "@/components/player/AudioContext";
import { TrackRow } from "@/components/ui/TrackRow";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { formatStreams } from "@/lib/utils/format";
import { getGradientForId } from "@/lib/utils/colors";

interface ArtistClientProps {
  artist: ArtistDetail;
}

export function ArtistClient({ artist }: ArtistClientProps) {
  const { playTrack, currentTrack, isPlaying } = useAudio();
  const gradient = getGradientForId(artist.id);

  const isCurrentArtistPlaying =
    isPlaying && artist.top_tracks.some((t) => t.id === currentTrack?.id);

  const handlePlayArtist = () => {
    if (artist.top_tracks.length > 0) {
      playTrack(artist.top_tracks[0], artist.top_tracks);
    }
  };

  return (
    <div className="space-y-8 select-none">
      {/* Hero Header */}
      <div
        className={`relative p-8 md:p-10 pt-16 bg-gradient-to-b ${gradient} flex flex-col md:flex-row md:items-end gap-6 shadow-inner`}
      >
        <img
          src={artist.image_url || "/placeholder-artist.png"}
          alt={artist.name}
          className="w-40 h-40 md:w-52 md:h-52 rounded-full object-cover shadow-2xl ring-4 ring-white/10 flex-shrink-0"
        />
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-white/90 uppercase tracking-widest">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>Benchmark Artist Profile</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-black text-white tracking-tight">
            {artist.name}
          </h1>
          <div className="flex flex-wrap items-center gap-3 text-xs sm:text-sm text-white/90">
            <span className="font-semibold text-white">
              {formatStreams(artist.total_streams)} benchmark streams (synthetic)
            </span>
            <span>•</span>
            <span className="font-mono bg-white/20 px-2 py-0.5 rounded text-xs">
              Popularity: {artist.popularity}/100
            </span>
            <span>•</span>
            <span>{artist.albums.length} releases</span>
          </div>
          {artist.genres.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {artist.genres.map((g) => (
                <Link
                  key={g}
                  href={`/search?genre=${encodeURIComponent(g)}`}
                  className="text-[11px] font-medium bg-black/40 hover:bg-black/60 text-white/90 px-2.5 py-0.5 rounded-full border border-white/10 transition-colors"
                >
                  {g}
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
        {/* Play Action Bar */}
        <div className="flex items-center gap-4">
          <button
            onClick={handlePlayArtist}
            className="w-14 h-14 rounded-full bg-primary hover:bg-primary-hover active:scale-95 text-black flex items-center justify-center shadow-xl transition-all"
            title={`Play ${artist.name}`}
          >
            <Play className="w-6 h-6 fill-black ml-0.5" />
          </button>
          <Link
            href={`/analytics`}
            className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-surface-elevated hover:bg-surface-highlight border border-white/10 text-white text-xs font-semibold"
          >
            <BarChart3 className="w-4 h-4 text-primary" />
            <span>View Artist in Analytics Studio</span>
          </Link>
        </div>

        {/* Top Tracks */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-4">Popular Tracks</h2>
          {artist.top_tracks.length > 0 ? (
            <div className="bg-surface/50 rounded-xl border border-white/5 divide-y divide-white/5 overflow-hidden">
              {artist.top_tracks.map((track, idx) => (
                <TrackRow
                  key={track.id}
                  track={track}
                  index={idx}
                  playlistQueue={artist.top_tracks}
                />
              ))}
            </div>
          ) : (
            <div className="text-xs text-muted">No tracks found for this artist.</div>
          )}
        </div>

        {/* Discography */}
        <div>
          <SectionHeader title="Discography" subtitle="Albums and singles by this artist" />
          {artist.albums.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {artist.albums.map((album) => (
                <Card
                  key={album.id}
                  title={album.title}
                  subtitle={`${album.release_date ? album.release_date.split("-")[0] : ""} • Album`}
                  imageUrl={album.cover_image_url}
                  href={`/album/${album.id}`}
                  type="album"
                />
              ))}
            </div>
          ) : (
            <div className="text-xs text-muted">No releases found.</div>
          )}
        </div>
      </div>
    </div>
  );
}
