"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Play, Sparkles, TrendingUp, Music, BarChart3, Disc, Users } from "lucide-react";
import { Track, Artist, Album, OverviewStats } from "@/lib/data/types";
import { useAudio } from "../player/AudioContext";
import { Card } from "../ui/Card";
import { TrackRow } from "../ui/TrackRow";
import { SectionHeader } from "../ui/SectionHeader";
import { formatStreams, formatNumber } from "@/lib/utils/format";
import { getGenreColor } from "@/lib/utils/colors";

interface HomeClientProps {
  quickPicks: Track[];
  topTracks: Track[];
  featuredArtists: Artist[];
  featuredAlbums: Album[];
  stats: OverviewStats;
  genres: string[];
}

export function HomeClient({
  quickPicks,
  topTracks,
  featuredArtists,
  featuredAlbums,
  stats,
  genres,
}: HomeClientProps) {
  const { playTrack, currentTrack, isPlaying } = useAudio();
  const [greeting, setGreeting] = useState("Good day");

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 18) setGreeting("Good afternoon");
    else setGreeting("Good evening");
  }, []);

  return (
    <div className="p-6 space-y-8 max-w-7xl mx-auto">
      {/* Hero Welcome & Quick Stats */}
      <div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              {greeting}
            </h1>
            <p className="text-sm text-muted mt-1">
              Benchmark Dataset: Synthetic music intelligence across {stats.total_tracks} tracks and {stats.total_artists} artists (Demonstration Data)
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/analytics"
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 hover:bg-emerald-500/20 text-primary border border-primary/30 text-xs font-bold transition-all shadow-sm"
            >
              <BarChart3 className="w-4 h-4" />
              <span>Launch Analytics Studio</span>
            </Link>
          </div>
        </div>

        {/* 6-Card Quick-Access Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {quickPicks.slice(0, 6).map((track) => {
            const isThisPlaying = currentTrack?.id === track.id && isPlaying;
            return (
              <div
                key={track.id}
                className="group flex items-center justify-between bg-surface-elevated hover:bg-surface-highlight rounded-md overflow-hidden transition-all duration-200 cursor-pointer shadow-sm pr-4 select-none"
                onClick={() => playTrack(track, quickPicks)}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <img
                    src={track.cover_image_url || "/placeholder-album.png"}
                    alt={track.title}
                    className="w-16 h-16 object-cover flex-shrink-0"
                  />
                  <div className="overflow-hidden">
                    <span className="font-semibold text-sm text-white truncate block">
                      {track.title}
                    </span>
                    <span className="text-xs text-muted truncate block">
                      {track.artist_name}
                    </span>
                  </div>
                </div>

                <button
                  className={`w-10 h-10 rounded-full bg-primary hover:bg-primary-hover active:scale-95 text-black flex items-center justify-center shadow-lg transition-all flex-shrink-0 ${
                    isThisPlaying
                      ? "opacity-100"
                      : "opacity-0 group-hover:opacity-100 translate-y-1 group-hover:translate-y-0"
                  }`}
                  title={`Play ${track.title}`}
                >
                  <Play className="w-4 h-4 fill-black ml-0.5" />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Dataset Highlights Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-surface p-4 rounded-xl border border-white/5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-primary">
            <Music className="w-5 h-5" />
          </div>
          <div>
            <div className="text-lg font-bold text-white font-mono">
              {stats.total_tracks}
            </div>
            <div className="text-xs text-muted">Benchmark Tracks</div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400">
            <Users className="w-5 h-5" />
          </div>
          <div>
            <div className="text-lg font-bold text-white font-mono">
              {stats.total_artists}
            </div>
            <div className="text-xs text-muted">Benchmark Artists</div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400">
            <Disc className="w-5 h-5" />
          </div>
          <div>
            <div className="text-lg font-bold text-white font-mono">
              {stats.total_albums}
            </div>
            <div className="text-xs text-muted">Benchmark Albums</div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <div className="text-lg font-bold text-white font-mono">
              {formatStreams(stats.total_streams)}
            </div>
            <div className="text-xs text-muted">Benchmark Streams</div>
          </div>
        </div>
      </div>

      {/* Popular Tracks Section */}
      <div>
        <SectionHeader
          title="Most Streamed Tracks"
          subtitle="Top ranked songs by synthetic benchmark streams (demonstration data)"
          href="/search"
          actionText="Explore all"
        />
        <div className="bg-surface/50 rounded-xl border border-white/5 divide-y divide-white/5 overflow-hidden">
          {topTracks.slice(0, 5).map((track, idx) => (
            <TrackRow
              key={track.id}
              track={track}
              index={idx}
              playlistQueue={topTracks}
            />
          ))}
        </div>
      </div>

      {/* Featured Artists */}
      <div>
        <SectionHeader
          title="Featured Artists"
          subtitle="Artists with highest synthetic stream engagement (demonstration data)"
          href="/library?tab=artists"
        />
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {featuredArtists.slice(0, 6).map((artist) => (
            <Card
              key={artist.id}
              title={artist.name}
              subtitle={`${formatStreams(artist.total_streams)} streams`}
              imageUrl={artist.image_url}
              href={`/artist/${artist.id}`}
              type="artist"
              badge={`Pop ${artist.popularity}`}
              onPlay={() => {
                const artistTopTrack = topTracks.find(
                  (t) => t.artist_id === artist.id
                );
                if (artistTopTrack) playTrack(artistTopTrack, topTracks);
              }}
            />
          ))}
        </div>
      </div>

      {/* Recommended Albums */}
      <div>
        <SectionHeader
          title="Popular Albums & Releases"
          subtitle="Recent full-length records and singles"
          href="/library?tab=albums"
        />
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {featuredAlbums.slice(0, 6).map((album) => (
            <Card
              key={album.id}
              title={album.title}
              subtitle={album.artist_name || "Various Artists"}
              imageUrl={album.cover_image_url}
              href={`/album/${album.id}`}
              type="album"
              onPlay={() => {
                const albumTrack = topTracks.find((t) => t.album_id === album.id);
                if (albumTrack) playTrack(albumTrack);
              }}
            />
          ))}
        </div>
      </div>

      {/* Trending Genres Shelf */}
      <div>
        <SectionHeader
          title="Explore Genres"
          subtitle="Jump directly into soundscapes"
          href="/search"
        />
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {genres.slice(0, 6).map((g) => {
            const color = getGenreColor(g);
            return (
              <Link
                key={g}
                href={`/search?genre=${encodeURIComponent(g)}`}
                className="relative h-24 rounded-lg p-3 overflow-hidden font-bold text-white text-base hover:scale-[1.02] active:scale-[0.98] transition-all shadow-md group"
                style={{ backgroundColor: color }}
              >
                <span>{g}</span>
                <div className="absolute -bottom-2 -right-2 w-16 h-16 rounded-full bg-black/20 group-hover:scale-125 transition-transform" />
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
