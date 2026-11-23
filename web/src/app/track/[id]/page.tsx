import { notFound } from "next/navigation";
import { repository } from "@/lib/data/repository";
import { TrackClient } from "@/components/track/TrackClient";

export const revalidate = 60;

interface TrackPageProps {
  params: Promise<{ id: string }>;
}

export default async function TrackPage({ params }: TrackPageProps) {
  const { id } = await params;
  const track = await repository.getTrackById(id);

  if (!track) {
    notFound();
  }

  return <TrackClient track={track} />;
}
