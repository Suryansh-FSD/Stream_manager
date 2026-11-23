import React, { Suspense } from "react";
import { repository } from "@/lib/data/repository";
import { LibraryClient } from "@/components/library/LibraryClient";

export const revalidate = 60;

export default async function LibraryPage() {
  const [allTracks, allArtists, allAlbums] = await Promise.all([
    repository.getTracks({ limit: 495 }),
    repository.getArtists({ limit: 18 }),
    repository.getAlbums({ limit: 40 }),
  ]);

  return (
    <Suspense
      fallback={
        <div className="p-6 text-muted text-sm flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-primary animate-ping" />
          Loading Library...
        </div>
      }
    >
      <LibraryClient
        allTracks={allTracks}
        allArtists={allArtists}
        allAlbums={allAlbums}
      />
    </Suspense>
  );
}
