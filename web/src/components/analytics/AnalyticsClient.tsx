"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  BarChart3,
  ExternalLink,
  Sparkles,
  Server,
  Layers,
  Activity,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Terminal,
} from "lucide-react";

const ANALYTICS_PAGES = [
  {
    title: "1. Overview",
    desc: "Executive metrics, key indicators, stream totals, and distribution summaries.",
    icon: Activity,
  },
  {
    title: "2. Artist Intelligence",
    desc: "Artist performance rankings, career trajectories, and multi-artist collaboration analysis.",
    icon: Layers,
  },
  {
    title: "3. Genre Intelligence",
    desc: "Acoustic fingerprints by genre, mood clustering, and popularity heatmaps.",
    icon: Sparkles,
  },
  {
    title: "4. Yearly Trends",
    desc: "Temporal evolution of danceability, energy, and acousticness across release years.",
    icon: BarChart3,
  },
  {
    title: "5. Audio Features",
    desc: "Interactive multi-dimensional radar comparison and acoustic metric inspection.",
    icon: Layers,
  },
  {
    title: "6. Correlation Analysis",
    desc: "Interactive Pearson & Spearman correlation heatmaps between audio metrics and streams.",
    icon: Activity,
  },
  {
    title: "7. Data Quality & Pipeline Health",
    desc: "Automated validation report, missing value audit, and cleaning pipeline diagnostics.",
    icon: CheckCircle2,
  },
];

export function AnalyticsClient() {
  const [streamlitUrl, setStreamlitUrl] = useState("http://localhost:8501");
  const [isOnline, setIsOnline] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [showIframe, setShowIframe] = useState(false);

  const checkHealth = useCallback(async () => {
    setIsChecking(true);
    try {
      await fetch(`${streamlitUrl}/_stcore/health`, {
        method: "GET",
        mode: "no-cors",
      });
      setIsOnline(true);
    } catch {
      setIsOnline(false);
    } finally {
      setIsChecking(false);
    }
  }, [streamlitUrl]);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Hero Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 p-8 rounded-2xl bg-gradient-to-r from-emerald-950/60 via-surface-elevated to-surface border border-primary/20 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-primary/20 text-primary border border-primary/30">
              Streamlit Studio
            </span>
            <div className="flex items-center gap-1.5 text-xs text-muted">
              <span
                className={`w-2 h-2 rounded-full ${
                  isOnline ? "bg-primary animate-pulse" : "bg-amber-400"
                }`}
              />
              <span>
                {isOnline === null
                  ? "Checking status..."
                  : isOnline
                  ? "Studio Server Online"
                  : "Studio Offline / Standby"}
              </span>
            </div>
          </div>
          <h1 className="text-3xl md:text-5xl font-black text-white tracking-tight">
            Spotify Trends Analytics Studio
          </h1>
          <p className="text-sm text-muted max-w-2xl">
            A comprehensive Python-powered data science platform with 7 analytical pages, Plotly
            charts, statistical correlation models, and dual Supabase/local data streaming.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <a
            href={streamlitUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-5 py-3 rounded-full bg-primary hover:bg-primary-hover active:scale-95 text-black font-bold text-sm shadow-xl shadow-primary/25 transition-all"
          >
            <span>Launch Studio</span>
            <ExternalLink className="w-4 h-4 stroke-[2.5]" />
          </a>

          <button
            onClick={() => setShowIframe(!showIframe)}
            className="flex items-center gap-2 px-4 py-3 rounded-full bg-surface-elevated hover:bg-surface-highlight border border-white/10 text-white text-xs font-semibold transition-colors"
          >
            <Server className="w-4 h-4 text-emerald-400" />
            <span>{showIframe ? "Hide Embedded Studio" : "Embed Studio in Page"}</span>
          </button>

          <button
            onClick={checkHealth}
            disabled={isChecking}
            className="p-3 rounded-full bg-surface-elevated hover:bg-surface-highlight border border-white/10 text-muted hover:text-white transition-colors"
            title="Check connection"
          >
            <RefreshCw className={`w-4 h-4 ${isChecking ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Embedded Iframe Option */}
      {showIframe && (
        <div className="rounded-2xl border border-white/10 overflow-hidden bg-black shadow-2xl">
          <div className="h-10 bg-surface px-4 flex items-center justify-between text-xs text-muted border-b border-white/5">
            <span className="font-mono">{streamlitUrl}</span>
            <a
              href={streamlitUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white flex items-center gap-1"
            >
              <span>Full Screen</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
          <iframe
            src={streamlitUrl}
            className="w-full h-[820px] min-h-[760px] border-none rounded-b-2xl"
            title="Streamlit Analytics Studio"
          />
        </div>
      )}

      {/* How to start Streamlit (if offline) */}
      {!isOnline && (
        <div className="p-6 rounded-xl bg-amber-500/10 border border-amber-500/20 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
            <Terminal className="w-4 h-4" />
            <span>Launch the local Streamlit Analytics server</span>
          </div>
          <p className="text-xs text-muted">
            The Next.js music platform is running. To activate the analytical dashboards, run the
            Streamlit app in your terminal:
          </p>
          <div className="p-3 bg-black/60 rounded-lg font-mono text-xs text-emerald-400 flex items-center justify-between">
            <code>source venv/bin/activate && streamlit run analytics/app.py</code>
            <button
              onClick={checkHealth}
              className="text-xs text-white hover:text-primary underline ml-4"
            >
              Check again
            </button>
          </div>
        </div>
      )}

      {/* Analytics Studio Feature Grid */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-white">Interactive Dashboards Available</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ANALYTICS_PAGES.map((page) => {
            const Icon = page.icon;
            return (
              <div
                key={page.title}
                className="p-5 rounded-xl bg-surface hover:bg-surface-elevated transition-colors border border-white/5 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="w-9 h-9 rounded-lg bg-emerald-500/10 text-primary flex items-center justify-center">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-white text-base">{page.title}</h3>
                  <p className="text-xs text-muted leading-relaxed">{page.desc}</p>
                </div>
                <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs text-muted">
                  <span className="font-mono text-[10px] text-emerald-400">Streamlit Page</span>
                  <a
                    href={streamlitUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-white flex items-center gap-1 font-semibold"
                  >
                    <span>Open</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
