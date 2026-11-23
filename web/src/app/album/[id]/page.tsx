import { notFound } from "next/navigation";
import { repository } from "@/lib/data/repository";
import { AlbumClient } from "@/components/album/AlbumClient";

export const revalidate = 60;

interface AlbumPageProps {
  params: Promise<{ id: string }>;
}

export default async function AlbumPage({ params }: AlbumPageProps) {
  const { id } = await params;
  const album = await repository.getAlbumById(id);

  if (!album) {
    notFound();
  }

  return <AlbumClient album={album} />;
}
