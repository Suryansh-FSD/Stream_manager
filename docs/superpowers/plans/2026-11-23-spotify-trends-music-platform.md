# Spotify Trends Music Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade, responsive Next.js music discovery and streaming application ("Spotify Trends") powered by the project's data engineering pipeline and Supabase backend, featuring a dark Spotify UI, real audio playback, rich metadata inspection, and integrated analytics navigation.

**Architecture:** A Next.js 15 App Router frontend located in `web/` with server and client components, backed by a unified Data Access Layer (`repository.ts`) that reads from local normalized Parquet/CSV files (`data/processed/`) when offline/uncredentialed and switches to Supabase PostgreSQL analytical views when configured. Global playback state is managed via React Context (`AudioContext`) driving an interactive persistent bottom player with synthesized audio preview fallback for instant listening.

**Tech Stack:** Next.js 15 (App Router), React 19 / 18, TypeScript, Tailwind CSS, Lucide React, Recharts, `@supabase/supabase-js`, `csv-parse`, Web Audio API.

**Spec:** Task 4 Prompt specification and system architecture documented in `README.md` and database migrations `supabase/migrations/001_initial_schema.sql`, `002_analytical_views.sql`.

## Global Constraints

- **Theme Palette**: Background `#121212`, elevated surfaces `#181818` and `#242424`, hover surfaces `#282828`, primary accent `#1DB954` (Spotify Green), primary text `#FFFFFF`, muted secondary text `#B3B3B3`.
- **Original Branding**: Distinctive **Spotify Trends** identity with customized waveforms / note iconography. Never use proprietary Spotify logos or copyrighted assets.
- **Dual Data Source**: Must function immediately out of the box with zero external configuration by reading normalized datasets from `../data/processed/`, while gracefully connecting to Supabase PostgreSQL when credentials exist.
- **Data Integrity**: Never invent stream counts, metrics, or relationships. Track streams must reflect actual numbers from `track_metrics`, and popularity scores must remain separate from stream counts.
- **Persistent Player**: Music playback must continue without interruption when navigating across pages (`/`, `/search`, `/library`, `/artist/[id]`, `/album/[id]`, `/track/[id]`, `/analytics`).
- **Streamlit Analytics Launcher**: Prominent navigation entry pointing to the Streamlit studio on `http://localhost:8501` (configurable via `NEXT_PUBLIC_ANALYTICS_URL`).

---

### Task 1: Initialize Next.js Workspace & Base Scaffolding

**Files:**
- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/tailwind.config.ts`
- Create: `web/postcss.config.mjs`
- Create: `web/next.config.ts`
- Create: `web/src/app/globals.css`
- Test: Build verification with `npm run build` or `next lint`

**Interfaces:**
- Produces: Functional Next.js build pipeline with Tailwind utility styling and Spotify dark design tokens.

- [ ] **Step 1: Create `web/package.json` with compatible stable dependencies**
- [ ] **Step 2: Create TypeScript, PostCSS, and Next.js configuration files**
- [ ] **Step 3: Create Tailwind CSS configuration with custom theme tokens (`#121212`, `#181818`, `#242424`, `#1DB954`)**
- [ ] **Step 4: Create `web/src/app/globals.css` with custom dark styling and scrollbars**
- [ ] **Step 5: Run `npm install` inside `web/` to resolve dependencies**
- [ ] **Step 6: Run `npm run build` or test compile to verify zero configuration errors**

---

### Task 2: Data Access Layer & Type Definitions

**Files:**
- Create: `web/src/lib/data/types.ts`
- Create: `web/src/lib/data/local-source.ts`
- Create: `web/src/lib/data/supabase-source.ts`
- Create: `web/src/lib/data/repository.ts`
- Create: `web/src/lib/utils/format.ts`
- Create: `web/src/lib/utils/colors.ts`
- Test: `web/scripts/test-repository.ts` or Node test runner

**Interfaces:**
- Produces:
  - `getTracks(query?: { limit?: number, genre?: string, sort?: string }): Promise<Track[]>`
  - `getTrackById(id: string): Promise<TrackDetail | null>`
  - `getArtists(query?: { limit?: number }): Promise<Artist[]>`
  - `getArtistById(id: string): Promise<ArtistDetail | null>`
  - `getAlbums(query?: { limit?: number }): Promise<Album[]>`
  - `getAlbumById(id: string): Promise<AlbumDetail | null>`
  - `searchAll(query: string): Promise<SearchResults>`
  - `getOverviewStats(): Promise<OverviewStats>`

- [ ] **Step 1: Define TypeScript schemas matching PostgreSQL migrations (`Track`, `Album`, `Artist`, `AudioFeatures`, `TrackMetrics`)**
- [ ] **Step 2: Implement `local-source.ts` parsing CSV files from `../data/processed/` with in-memory caching**
- [ ] **Step 3: Implement `supabase-source.ts` with Supabase client fallback**
- [ ] **Step 4: Implement unified `repository.ts` routing between Supabase and local data**
- [ ] **Step 5: Implement `format.ts` for duration formatting (`m:ss`) and stream counts (`1.2M`, `500K`)**
- [ ] **Step 6: Create verification test script and execute to ensure 495 tracks, 18 artists, and 357 albums load cleanly**

---

### Task 3: Global Audio Playback Engine & AudioContext

**Files:**
- Create: `web/src/lib/audio-synth.ts`
- Create: `web/src/components/player/AudioContext.tsx`
- Create: `web/src/components/layout/Player.tsx`
- Test: Verify state changes, play/pause toggles, and volume scrubbing in isolation

**Interfaces:**
- Consumes: `Track` interface
- Produces: `useAudioPlayer()` hook with `{ currentTrack, isPlaying, playTrack, pauseTrack, togglePlay, progress, duration, seek, volume, setVolume, queue, nextTrack, prevTrack, isMuted, toggleMute }`

- [ ] **Step 1: Implement `audio-synth.ts` using Web Audio API to generate harmonious preview chords when track `preview_url` is not set**
- [ ] **Step 2: Implement `AudioContext.tsx` managing HTML5 Audio + Web Audio playback, track queue, and shuffle/repeat logic**
- [ ] **Step 3: Build `Player.tsx` bottom bar with album thumbnail, title, artist, playback buttons, progress scrubber, and volume control**
- [ ] **Step 4: Verify play/pause and progress scrubbing without re-rendering parent tree**

---

### Task 4: Layout Shell (Sidebar, TopBar, and Navigation)

**Files:**
- Create: `web/src/components/layout/Sidebar.tsx`
- Create: `web/src/components/layout/TopBar.tsx`
- Create: `web/src/app/layout.tsx`
- Test: Responsive viewport testing (desktop collapsible, mobile drawer)

**Interfaces:**
- Produces: Persistent shell holding Sidebar (Home, Search, Library, Analytics Studio), TopBar (history buttons, search pill, user indicator), and bottom Player.

- [ ] **Step 1: Build `Sidebar.tsx` with Spotify Trends branding, navigation links, quick-access library shortcuts, and Analytics Studio CTA**
- [ ] **Step 2: Build `TopBar.tsx` with browser back/forward buttons, search bar integration, and external GitHub/Supabase status indicator**
- [ ] **Step 3: Wire `layout.tsx` wrapping the application in `AudioProvider` with full-height flex column and responsive layout**

---

### Task 5: Reusable UI Components

**Files:**
- Create: `web/src/components/ui/Card.tsx`
- Create: `web/src/components/ui/TrackRow.tsx`
- Create: `web/src/components/ui/Badge.tsx`
- Create: `web/src/components/ui/SectionHeader.tsx`
- Create: `web/src/components/ui/AudioFeatureRadar.tsx`

**Interfaces:**
- Produces:
  - `<Card title subtitle image type="album"|"artist" onPlay />`
  - `<TrackRow track index isCurrent isPlaying onPlay />`
  - `<AudioFeatureRadar features={danceability, energy, valence, ...} />`

- [ ] **Step 1: Build `Card.tsx` with subtle hover lift, Spotify green floating play button, and responsive image loading**
- [ ] **Step 2: Build `TrackRow.tsx` table row with track number hover play state, title, duration, streams, and explicit badge**
- [ ] **Step 3: Build `AudioFeatureRadar.tsx` using Recharts RadarChart / BarChart for visualizing audio attributes**
- [ ] **Step 4: Build `SectionHeader.tsx` with title and action links**

---

### Task 6: Home Page (`/`) Implementation

**Files:**
- Create: `web/src/app/page.tsx`
- Test: Home page render test with live dataset

**Interfaces:**
- Consumes: `repository.getOverviewStats()`, `repository.getTracks()`, `repository.getArtists()`, `repository.getAlbums()`

- [ ] **Step 1: Implement greeting header ("Good morning / afternoon / evening") based on local client time**
- [ ] **Step 2: Build 6-card "Recently Played" quick-access grid with instant play button**
- [ ] **Step 3: Implement "Popular Tracks" horizontal shelf and compact listing**
- [ ] **Step 4: Implement "Featured Artists" circular avatar cards**
- [ ] **Step 5: Implement "Recommended Albums" and "Trending Genres" carousels**
- [ ] **Step 6: Verify full SSR/SSG rendering without client hydration mismatch**

---

### Task 7: Search & Discovery Page (`/search`)

**Files:**
- Create: `web/src/app/search/page.tsx`
- Test: Search query tests across track titles, artist names, albums, and genres

**Interfaces:**
- Consumes: `repository.searchAll(query)`

- [ ] **Step 1: Implement interactive search input with debounce (150ms)**
- [ ] **Step 2: Build Genre Discovery grid (colorful curated cards) for empty search state**
- [ ] **Step 3: Build Search Results view categorized by Top Result, Songs, Artists, and Albums**
- [ ] **Step 4: Implement empty / no-results states with helpful search suggestions**

---

### Task 8: Your Library Page (`/library`)

**Files:**
- Create: `web/src/app/library/page.tsx`
- Test: Filter tabs (All, Playlists, Artists, Albums), liked songs list

**Interfaces:**
- Consumes: Local storage / session library state + repository data

- [ ] **Step 1: Implement Library tabs (All, Liked Songs, Artists, Albums)**
- [ ] **Step 2: Implement "Liked Songs" default playlist with dynamic track count and duration**
- [ ] **Step 3: Display saved/favorite artists and albums with grid and list toggle**
- [ ] **Step 4: Add clear empty states explaining client-side storage persistence**

---

### Task 9: Entity Detail Pages (`/artist/[id]`, `/album/[id]`, `/track/[id]`)

**Files:**
- Create: `web/src/app/artist/[id]/page.tsx`
- Create: `web/src/app/album/[id]/page.tsx`
- Create: `web/src/app/track/[id]/page.tsx`
- Test: Route validation with dataset IDs (e.g. `cdb526ca-beca-5193-a8ef-5dd5ff3518b4`, `synth_track_0446`)

**Interfaces:**
- Consumes: `repository.getArtistById(id)`, `repository.getAlbumById(id)`, `repository.getTrackById(id)`

- [ ] **Step 1: Build `artist/[id]` with hero banner, verified badge, monthly streams, top 5 tracks, and albums grid**
- [ ] **Step 2: Build `album/[id]` with album artwork, metadata, full track listing table, and total runtime**
- [ ] **Step 3: Build `track/[id]` with track metadata, popularity gauge, actual stream count, and interactive audio features radar**
- [ ] **Step 4: Implement 404 / Not Found fallbacks for invalid IDs**

---

### Task 10: Analytics Studio Integration (`/analytics`)

**Files:**
- Create: `web/src/app/analytics/page.tsx`
- Test: Embedded launcher and iframe status ping

**Interfaces:**
- Displays: Dedicated launcher dashboard with live status indicator for Streamlit (`http://localhost:8501`), quick stats preview, "Open in New Tab" CTA, and embedded iframe fallback.

- [ ] **Step 1: Implement healthcheck pinger to `http://localhost:8501/_stcore/health`**
- [ ] **Step 2: Build studio overview card highlighting the 7 analytics pages (Overview, Artist Intelligence, etc.)**
- [ ] **Step 3: Provide embedded iframe toggle when local Streamlit is active**
- [ ] **Step 4: Display startup guide (`streamlit run analytics/app.py`) when Streamlit server is offline**

---

### Task 11: Production Build, End-to-End Verification & Documentation

**Files:**
- Modify: `README.md`
- Test: `npm run build && npm run lint` in `web/`

- [ ] **Step 1: Run full production Next.js build (`next build`) and resolve any TypeScript or lint warnings**
- [ ] **Step 2: Verify responsive design on mobile (375px), tablet (768px), and desktop (1280px)**
- [ ] **Step 3: Test audio playback continuity while clicking through all routes**
- [ ] **Step 4: Update `README.md` with Next.js development and production run instructions**
- [ ] **Step 5: Check `git status` to ensure all files are cleanly tracked**
