export function formatDuration(ms: number): string {
  if (!ms || isNaN(ms)) return "0:00";
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
}

export function formatDurationLong(ms: number): string {
  if (!ms || isNaN(ms)) return "0 min";
  const totalMinutes = Math.floor(ms / (1000 * 60));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours > 0) {
    return `${hours} hr ${minutes} min`;
  }
  return `${minutes} min`;
}

export function formatStreams(streams: number | undefined): string {
  if (streams === undefined || streams === null || isNaN(streams)) return "0";
  if (streams >= 1_000_000_000) {
    return (streams / 1_000_000_000).toFixed(1) + "B";
  }
  if (streams >= 1_000_000) {
    return (streams / 1_000_000).toFixed(1) + "M";
  }
  if (streams >= 1_000) {
    return (streams / 1_000).toFixed(1) + "K";
  }
  return streams.toLocaleString();
}

export function formatNumber(num: number | undefined): string {
  if (num === undefined || num === null || isNaN(num)) return "0";
  return num.toLocaleString();
}

export function formatDate(dateStr: string | null): string {
  if (!dateStr) return "Unknown Date";
  try {
    const parts = dateStr.split("-");
    if (parts.length === 1) return parts[0];
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: parts.length === 3 ? "numeric" : undefined,
    });
  } catch {
    return dateStr;
  }
}
