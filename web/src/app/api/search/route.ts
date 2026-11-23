import { NextRequest, NextResponse } from "next/server";
import { repository } from "@/lib/data/repository";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const q = searchParams.get("q") || "";
  const genre = searchParams.get("genre");

  try {
    if (genre) {
      const tracks = await repository.getTracks({ genre, limit: 30 });
      return NextResponse.json({
        query: genre,
        tracks,
        artists: [],
        albums: [],
        genres: [genre],
      });
    }

    const results = await repository.searchAll(q);
    return NextResponse.json(results);
  } catch (error: any) {
    console.error("Search API error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
