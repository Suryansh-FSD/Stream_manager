"use client";

import React from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { AudioFeatures } from "@/lib/data/types";

interface AudioFeatureRadarProps {
  features?: AudioFeatures | null;
}

export function AudioFeatureRadar({ features }: AudioFeatureRadarProps) {
  if (!features) {
    return (
      <div className="h-64 flex items-center justify-center text-xs text-muted">
        No audio features available for this track.
      </div>
    );
  }

  const data = [
    { subject: "Danceability", value: Math.round(features.danceability * 100), fullMark: 100 },
    { subject: "Energy", value: Math.round(features.energy * 100), fullMark: 100 },
    { subject: "Valence", value: Math.round(features.valence * 100), fullMark: 100 },
    { subject: "Acousticness", value: Math.round(features.acousticness * 100), fullMark: 100 },
    { subject: "Speechiness", value: Math.round(features.speechiness * 100), fullMark: 100 },
    { subject: "Liveness", value: Math.round(features.liveness * 100), fullMark: 100 },
    { subject: "Instrumental", value: Math.round(features.instrumentalness * 100), fullMark: 100 },
  ];

  return (
    <div className="w-full h-72 relative">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="#333333" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: "#b3b3b3", fontSize: 11, fontFamily: "sans-serif" }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            stroke="#444444"
            tick={{ fill: "#666666", fontSize: 9 }}
          />
          <Radar
            name="Audio Profile"
            dataKey="value"
            stroke="#1DB954"
            fill="#1DB954"
            fillOpacity={0.4}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#181818",
              borderColor: "#333333",
              borderRadius: "8px",
              color: "#ffffff",
              fontSize: "12px",
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
