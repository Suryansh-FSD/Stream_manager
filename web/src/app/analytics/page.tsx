import React from "react";
import { AnalyticsClient } from "@/components/analytics/AnalyticsClient";

export const metadata = {
  title: "Analytics Studio | Spotify Trends",
  description:
    "Launch and explore the Python-powered Spotify Trends Streamlit Analytics Studio.",
};

export default function AnalyticsPage() {
  return <AnalyticsClient />;
}
