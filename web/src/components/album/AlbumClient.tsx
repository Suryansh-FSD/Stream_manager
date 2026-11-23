"use client";

import React from "react";
import Link from "next/link";
import { Play, Disc, Clock, Calendar } from "lucide-react";
import { AlbumDetail, Track } from "@/lib/data/types";
import { useAudio } from "@/components/player/AudioContext";
import { TrackRow } from "@/components/ui/TrackRow";
import { formatDurationLong, formatDate } from "@/lib/utils/format";
import { getGradientForId } from "@/lib/utils/colors";

interface AlbumClientProps {
  album: AlbumDetail;
}

export function AlbumClient({ album }: AlbumClientProps) {
  const { playTrack } = useAudio();
  const gradient = getGradientForId(album.id);

  const totalDurationMs = album.tracks.reduce((acc, t) => acc + t.duration_ms, 0);

  const handlePlayAlbum = () => {
    if (album.tracks.length > 0) {
      playTrack(album.tracks[0], album.tracks);
    }
  };

  return (
    <div className="space-y-6 select-none">
      {/* Hero Header */}
      <div
        className={`p-8 md:p-10 pt-16 bg-gradient-to-b ${gradient} flex flex-col md:flex-row md:items-end gap-6 shadow-inner`}
      >
        <img
          src={album.cover_image_url || "/placeholder-album.png"}
          alt={album.title}
          className="w-44 h-44 md:w-56 md:h-56 rounded-lg object-cover shadow-2xl flex-shrink-0 ring-1 ring-white/10"
        />
        <div className="space-y-2">
          <span className="text-xs uppercase font-bold tracking-wider text-white/80">
            Album
          </span>
          <h1 className="text-3xl md:text-5xl font-black text-white tracking-tight">
            {album.title}
          </h1>
          <div className="flex flex-wrap items-center gap-2 text-xs sm:text-sm text-white/90">
            {album.artist_id ? (
              <Link
                href={`/artist/${album.artist_id}`}
                className="font-bold text-white hover:underline"
              >
                {album.artist_name || "Unknown Artist"}
              </Link>
            ) : (
              <span className="font-bold text-white">{album.artist_name || "Unknown Artist"}</span>
            )}
            <span>•</span>
            <span>{album.release_date ? album.release_date.split("-")[0] : "Recent"}</span>
            <span>•</span>
            <span>
              {album.tracks.length} song{album.tracks.length === 1 ? "" : "s"},
            </span>
            <span className="text-muted-light">{formatDurationLong(totalDurationMs)}</span>
          </div>
        </div>
      </div>

      <div className="p-6 md:p-8 space-y-6 max-w-7xl mx-auto">
        {/* Play Action Bar */}
        <div className="flex items-center gap-4">
          <button
            onClick={handlePlayAlbum}
            className="w-14 h-14 rounded-full bg-primary hover:bg-primary-hover active:scale-95 text-black flex items-center justify-center shadow-xl transition-all"
            title={`Play ${album.title}`}
          >
            <Play className="w-6 h-6 fill-black ml-0.5" />
          </button>
        </div>

        {/* Tracks List */}
        <div className="bg-surface/50 rounded-xl border border-white/5 divide-y divide-white/5 overflow-hidden">
          {album.tracks.map((track, idx) => (
            <TrackRow
              key={track.id}
              track={track}
              index={idx}
              playlistQueue={album.tracks}
              showAlbum={false}
              showCover={false}
            />
          ))}
        </div>

        {/* Release Metadata Footnote */}
        <div className="text-xs text-muted pt-4 space-y-1">
          <div className="flex items-center gap-2">
            <Calendar className="w-3.5 h-3.5" />
            <span>Released {formatDate(album.release_date)}</span>
          </div>
          <div>© Spotify Trends Synthetic Record Catalog</div>
        </div>
      </div>
    </div>
  );
}
