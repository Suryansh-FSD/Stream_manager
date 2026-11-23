"use client";

import React, { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Heart, Play, Music, Users, Disc3, PlusCircle } from "lucide-react";
import { Track, Artist, Album } from "@/lib/data/types";
import { useAudio } from "@/components/player/AudioContext";
import { TrackRow } from "@/components/ui/TrackRow";
import { Card } from "@/components/ui/Card";
import { formatDurationLong } from "@/lib/utils/format";

interface LibraryClientProps {
  allTracks: Track[];
  allArtists: Artist[];
  allAlbums: Album[];
}

export function LibraryClient({
  allTracks,
  allArtists,
  allAlbums,
}: LibraryClientProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tabParam = searchParams.get("tab") || "all";
  const [activeTab, setActiveTab] = useState<string>(tabParam);

  const { likedTrackIds, playTrack } = useAudio();

  useEffect(() => {
    setActiveTab(tabParam);
  }, [tabParam]);

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    router.push(`/library?tab=${tab}`);
  };

  // Resolve liked tracks objects from allTracks
  const likedTracks = allTracks.filter((t) => likedTrackIds.has(t.id));
  const totalLikedDurationMs = likedTracks.reduce((acc, t) => acc + t.duration_ms, 0);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 select-none">
      {/* Library Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-white/5 pb-4">
        {[
          { id: "all", label: "All" },
          { id: "liked", label: "Liked Songs" },
          { id: "artists", label: "Artists" },
          { id: "albums", label: "Albums" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabChange(tab.id)}
            className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-colors ${
              activeTab === tab.id
                ? "bg-white text-black"
                : "bg-surface-elevated text-muted hover:text-white hover:bg-surface-highlight"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Liked Songs Hero / View (shown in 'all' or 'liked') */}
      {(activeTab === "all" || activeTab === "liked") && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-purple-900/60 via-indigo-900/40 to-surface-elevated border border-white/10">
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-600 to-emerald-400 flex items-center justify-center shadow-2xl flex-shrink-0">
                <Heart className="w-10 h-10 fill-white text-white" />
              </div>
              <div>
                <span className="text-xs uppercase font-bold tracking-wider text-white/60">
                  Playlist
                </span>
                <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight mt-0.5">
                  Liked Songs
                </h1>
                <p className="text-xs text-muted mt-1.5">
                  Spotify Trends Curator • {likedTracks.length} song{likedTracks.length === 1 ? "" : "s"}
                  {likedTracks.length > 0 && ` • ${formatDurationLong(totalLikedDurationMs)}`}
                </p>
              </div>
            </div>

            {likedTracks.length > 0 && (
              <button
                onClick={() => playTrack(likedTracks[0], likedTracks)}
                className="w-12 h-12 rounded-full bg-primary hover:bg-primary-hover active:scale-95 text-black flex items-center justify-center shadow-xl transition-transform"
                title="Play all liked songs"
              >
                <Play className="w-5 h-5 fill-black ml-0.5" />
              </button>
            )}
          </div>

          {/* Liked songs list */}
          {likedTracks.length > 0 ? (
            <div className="bg-surface/50 rounded-xl border border-white/5 divide-y divide-white/5 overflow-hidden">
              {likedTracks.map((track, idx) => (
                <TrackRow
                  key={track.id}
                  track={track}
                  index={idx}
                  playlistQueue={likedTracks}
                />
              ))}
            </div>
          ) : (
            <div className="p-8 text-center bg-surface/30 rounded-xl border border-dashed border-white/10">
              <Heart className="w-10 h-10 mx-auto text-muted/40 mb-3" />
              <h3 className="text-base font-bold text-white mb-1">Songs you like will appear here</h3>
              <p className="text-xs text-muted max-w-sm mx-auto mb-4">
                Save songs by tapping the heart icon on any song row or in the bottom player.
              </p>
              <Link
                href="/"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-elevated hover:bg-surface-highlight text-white text-xs font-semibold"
              >
                Find songs to like
              </Link>
            </div>
          )}
        </div>
      )}

      {/* Artists Tab */}
      {(activeTab === "all" || activeTab === "artists") && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">Artists Catalog</h2>
            <span className="text-xs text-muted">{allArtists.length} artists</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {allArtists.map((artist) => (
              <Card
                key={artist.id}
                title={artist.name}
                subtitle={`${artist.genres.slice(0, 2).join(", ") || "Artist"}`}
                imageUrl={artist.image_url}
                href={`/artist/${artist.id}`}
                type="artist"
              />
            ))}
          </div>
        </div>
      )}

      {/* Albums Tab */}
      {(activeTab === "all" || activeTab === "albums") && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">Albums Catalog</h2>
            <span className="text-xs text-muted">{allAlbums.length} albums</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {allAlbums.slice(0, 24).map((album) => (
              <Card
                key={album.id}
                title={album.title}
                subtitle={album.artist_name || "Album"}
                imageUrl={album.cover_image_url}
                href={`/album/${album.id}`}
                type="album"
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
