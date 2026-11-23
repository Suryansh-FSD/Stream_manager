import { repository } from "@/lib/data/repository";
import { HomeClient } from "@/components/home/HomeClient";

export const revalidate = 60; // 1 minute revalidation

export default async function HomePage() {
  const [topTracks, featuredArtists, featuredAlbums, stats] = await Promise.all([
    repository.getTracks({ sort: "streams", limit: 20 }),
    repository.getArtists({ sort: "streams", limit: 12 }),
    repository.getAlbums({ limit: 12 }),
    repository.getOverviewStats(),
  ]);

  // Extract top distinct genres
  const genreSet = new Set<string>();
  featuredArtists.forEach((a) => a.genres.forEach((g) => genreSet.add(g)));
  const genres = Array.from(genreSet);

  return (
    <HomeClient
      quickPicks={topTracks.slice(0, 6)}
      topTracks={topTracks}
      featuredArtists={featuredArtists}
      featuredAlbums={featuredAlbums}
      stats={stats}
      genres={genres}
    />
  );
}
