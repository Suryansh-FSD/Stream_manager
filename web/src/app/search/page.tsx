import React, { Suspense } from "react";
import { SearchClient } from "@/components/search/SearchClient";

export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <div className="p-6 text-muted text-sm flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-primary animate-ping" />
          Loading Search...
        </div>
      }
    >
      <SearchClient />
    </Suspense>
  );
}
