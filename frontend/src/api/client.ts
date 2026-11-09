import {
  Ad,
  Competitor,
  HealthStatus,
  MarketInsight,
  PosterPromptResponse,
  PosterRenderResponse,
} from "../types";

const API_BASE = "/api/v1";

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function fetchCompetitors(city?: string): Promise<Competitor[]> {
  const url = city ? `${API_BASE}/competitors?city=${encodeURIComponent(city)}` : `${API_BASE}/competitors`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch competitors");
  return res.json();
}

export async function addCompetitor(payload: { name: string; course?: string; city?: string; fb_page_url?: string }): Promise<Competitor> {
  const res = await fetch(`${API_BASE}/competitors`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to add competitor");
  return res.json();
}

export async function resolveCompetitorPage(inputText: string): Promise<{ resolved_name: string; resolved_page_id: string; confidence: string }> {
  const res = await fetch(`${API_BASE}/competitors/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input_text: inputText }),
  });
  if (!res.ok) throw new Error("Failed to resolve Page ID");
  return res.json();
}

export async function fetchAds(params: {
  competitorIds?: number[];
  course?: string;
  sortBy?: string;
}): Promise<Ad[]> {
  const query = new URLSearchParams();
  if (params.competitorIds && params.competitorIds.length > 0) {
    query.set("competitor_ids", params.competitorIds.join(","));
  }
  if (params.course && params.course !== "All") {
    query.set("course", params.course);
  }
  if (params.sortBy) {
    query.set("sort_by", params.sortBy);
  }

  const res = await fetch(`${API_BASE}/ads?${query.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch ads");
  return res.json();
}

export async function fetchMarketInsights(city: string = "Coimbatore"): Promise<MarketInsight> {
  const res = await fetch(`${API_BASE}/ads/insights/market?city=${encodeURIComponent(city)}`);
  if (!res.ok) throw new Error("Failed to fetch market insights");
  return res.json();
}

export async function refreshAds(): Promise<{ message: string; total_ads_collected: number }> {
  const res = await fetch(`${API_BASE}/ads/refresh`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to refresh ads");
  return res.json();
}

export async function analyzeAd(adId: number) {
  const res = await fetch(`${API_BASE}/ads/${adId}/analyze`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to analyze ad");
  return res.json();
}

export async function generatePosterPrompt(payload: {
  ad_id: number;
  course: string;
  angle_index: number;
  size_format: string;
}): Promise<PosterPromptResponse> {
  const res = await fetch(`${API_BASE}/posters/prompt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to generate poster prompt");
  return res.json();
}

export async function renderPoster(payload: {
  ad_id: number;
  course: string;
  angle_index: number;
  size_format: string;
}): Promise<PosterRenderResponse> {
  const res = await fetch(`${API_BASE}/posters/render`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to render poster");
  return res.json();
}
