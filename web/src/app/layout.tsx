import type { Metadata } from "next";
import "./globals.css";
import { AudioProvider } from "@/components/player/AudioContext";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { Player } from "@/components/layout/Player";

export const metadata: Metadata = {
  title: "Spotify Trends | Music Discovery & Analytics Platform",
  description:
    "A premium music discovery and listening experience combined with deep data intelligence.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-background text-white antialiased min-h-screen selection:bg-primary selection:text-black">
        <AudioProvider>
          <div className="flex h-screen overflow-hidden">
            {/* Left Persistent Navigation Sidebar */}
            <Sidebar />

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
              <TopBar />
              <main className="flex-1 overflow-y-auto pb-24 scroll-smooth">
                {children}
              </main>
            </div>
          </div>

          {/* Persistent Bottom Audio Player */}
          <Player />
        </AudioProvider>
      </body>
    </html>
  );
}
