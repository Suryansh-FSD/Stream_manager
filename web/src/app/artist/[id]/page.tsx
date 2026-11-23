import { notFound } from "next/navigation";
import { repository } from "@/lib/data/repository";
import { ArtistClient } from "@/components/artist/ArtistClient";

export const revalidate = 60;

interface ArtistPageProps {
  params: Promise<{ id: string }>;
}

export default async function ArtistPage({ params }: ArtistPageProps) {
  const { id } = await params;
  const artist = await repository.getArtistById(id);

  if (!artist) {
    notFound();
  }

  return <ArtistClient artist={artist} />;
}
