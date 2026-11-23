"use client";

import React, { useState, useEffect, useTransition } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Search as SearchIcon, X, Play, Music, Users, Disc3, Sparkles } from "lucide-react";
import { Track, Artist, Album, SearchResults } from "@/lib/data/types";
import { useAudio } from "@/components/player/AudioContext";
import { TrackRow } from "@/components/ui/TrackRow";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { getGenreColor } from "@/lib/utils/colors";
import { formatStreams } from "@/lib/utils/format";

const ALL_GENRES = [
  "Dream Pop",
  "Lo-Fi Beats",
  "Deep House",
  "Ambient",
  "R&B",
  "Electronic",
  "Indie Pop",
  "Synthwave",
  "Future Bass",
  "Alternative Rock",
  "Pop",
  "Rock",
];

export function SearchClient() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialQuery = searchParams.get("q") || "";
  const initialGenre = searchParams.get("genre") || "";

  const [query, setQuery] = useState(initialQuery);
  const [activeGenre, setActiveGenre] = useState(initialGenre);
  const [results, setResults] = useState<SearchResults | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isPending, startTransition] = useTransition();

  const { playTrack } = useAudio();

  // Perform search fetch
  const performSearch = async (searchTerm: string, genreTerm?: string) => {
    if (!searchTerm && !genreTerm) {
      setResults(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    try {
      const url = genreTerm
        ? `/api/search?genre=${encodeURIComponent(genreTerm)}`
        : `/api/search?q=${encodeURIComponent(searchTerm)}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setResults(data);
      }
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Sync with URL params
  useEffect(() => {
    const q = searchParams.get("q") || "";
    const g = searchParams.get("genre") || "";
    setQuery(q);
    setActiveGenre(g);
    if (q || g) {
      performSearch(q, g);
    } else {
      setResults(null);
    }
  }, [searchParams]);

  // Debounced input change
  const handleInputChange = (val: string) => {
    setQuery(val);
    setActiveGenre("");
    if (!val.trim()) {
      router.push("/search");
      setResults(null);
      return;
    }
    const timer = setTimeout(() => {
      startTransition(() => {
        router.push(`/search?q=${encodeURIComponent(val.trim())}`);
      });
    }, 200);
    return () => clearTimeout(timer);
  };

  const handleClear = () => {
    setQuery("");
    setActiveGenre("");
    setResults(null);
    router.push("/search");
  };

  const topResultTrack = results?.tracks && results.tracks.length > 0 ? results.tracks[0] : null;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8 select-none">
      {/* Search Input Box */}
      <div className="max-w-xl">
        <div className="relative">
          <SearchIcon className="w-5 h-5 text-muted absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search songs, artists, albums, or genres..."
            value={query}
            onChange={(e) => handleInputChange(e.target.value)}
            className="w-full bg-surface-elevated hover:bg-surface-highlight focus:bg-surface-highlight text-white text-base rounded-full pl-12 pr-10 py-3.5 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all placeholder:text-muted"
            autoFocus
          />
          {(query || activeGenre) && (
            <button
              onClick={handleClear}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-muted hover:text-white p-1"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Genre Filter Banner (when active) */}
      {activeGenre && (
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted uppercase font-bold tracking-wider">
            Filtered by Genre:
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-primary text-black">
            {activeGenre}
          </span>
          <button
            onClick={handleClear}
            className="text-xs text-muted hover:text-white underline ml-2"
          >
            Clear filter
          </button>
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="flex items-center justify-center py-20 text-muted gap-3">
          <span className="w-2 h-2 rounded-full bg-primary animate-ping" />
          <span className="text-sm">Searching Spotify Trends database...</span>
        </div>
      )}

      {/* Empty State: Browse All Categories / Genre Discovery */}
      {!isLoading && !results && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold tracking-tight text-white">Browse All</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {ALL_GENRES.map((genre) => {
              const bg = getGenreColor(genre);
              return (
                <button
                  key={genre}
                  onClick={() => {
                    setActiveGenre(genre);
                    router.push(`/search?genre=${encodeURIComponent(genre)}`);
                  }}
                  className="relative h-28 rounded-lg p-3 overflow-hidden text-left font-bold text-white text-lg hover:scale-[1.03] active:scale-[0.98] transition-transform shadow-md group"
                  style={{ backgroundColor: bg }}
                >
                  <span className="relative z-10">{genre}</span>
                  <div className="absolute -bottom-2 -right-2 w-20 h-20 rounded-full bg-black/20 group-hover:scale-125 transition-transform" />
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Results State */}
      {!isLoading && results && (
        <div className="space-y-8">
          {/* Top Result + Songs split */}
          {results.tracks.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Top Result Card */}
              {topResultTrack && (
                <div className="lg:col-span-1">
                  <h3 className="text-xl font-bold text-white mb-4">Top result</h3>
                  <div className="group relative p-5 rounded-xl bg-surface hover:bg-surface-elevated transition-colors flex flex-col justify-between h-56 select-none">
                    <div className="flex flex-col gap-3">
                      <img
                        src={topResultTrack.cover_image_url || "/placeholder-album.png"}
                        alt={topResultTrack.title}
                        className="w-20 h-20 rounded-md object-cover shadow-lg"
                      />
                      <div>
                        <Link
                          href={`/track/${topResultTrack.id}`}
                          className="text-2xl font-extrabold text-white hover:underline truncate block"
                        >
                          {topResultTrack.title}
                        </Link>
                        <p className="text-sm text-muted mt-0.5">
                          Song •{" "}
                          <span className="text-white">
                            {topResultTrack.artist_name || "Unknown Artist"}
                          </span>
                        </p>
                      </div>
                    </div>

                    {/* Floating Play Button */}
                    <button
                      onClick={() => playTrack(topResultTrack, results.tracks)}
                      className="absolute bottom-5 right-5 w-12 h-12 rounded-full bg-primary hover:bg-primary-hover active:scale-95 text-black flex items-center justify-center shadow-xl opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-200"
                      title="Play top result"
                    >
                      <Play className="w-5 h-5 fill-black ml-0.5" />
                    </button>
                  </div>
                </div>
              )}

              {/* Songs List */}
              <div className="lg:col-span-2">
                <h3 className="text-xl font-bold text-white mb-4">Songs</h3>
                <div className="bg-surface/50 rounded-xl border border-white/5 divide-y divide-white/5 overflow-hidden">
                  {results.tracks.slice(0, 4).map((track, idx) => (
                    <TrackRow
                      key={track.id}
                      track={track}
                      index={idx}
                      playlistQueue={results.tracks}
                      showAlbum={false}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* More Songs if > 4 */}
          {results.tracks.length > 4 && (
            <div>
              <SectionHeader title="More Songs" />
              <div className="bg-surface/50 rounded-xl border border-white/5 divide-y divide-white/5 overflow-hidden">
                {results.tracks.slice(4, 14).map((track, idx) => (
                  <TrackRow
                    key={track.id}
                    track={track}
                    index={idx + 4}
                    playlistQueue={results.tracks}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Artists */}
          {results.artists.length > 0 && (
            <div>
              <SectionHeader title="Artists" />
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {results.artists.map((artist) => (
                  <Card
                    key={artist.id}
                    title={artist.name}
                    subtitle="Artist"
                    imageUrl={artist.image_url}
                    href={`/artist/${artist.id}`}
                    type="artist"
                  />
                ))}
              </div>
            </div>
          )}

          {/* Albums */}
          {results.albums.length > 0 && (
            <div>
              <SectionHeader title="Albums" />
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {results.albums.map((album) => (
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

          {/* No results */}
          {results.tracks.length === 0 &&
            results.artists.length === 0 &&
            results.albums.length === 0 && (
              <div className="py-20 text-center">
                <h3 className="text-xl font-bold text-white mb-2">
                  No results found for &ldquo;{query || activeGenre}&rdquo;
                </h3>
                <p className="text-sm text-muted max-w-md mx-auto">
                  Please check the spelling or try searching for a different keyword, artist name,
                  album, or genre.
                </p>
              </div>
            )}
        </div>
      )}
    </div>
  );
}
