import {
  Ad,
  BusinessProfile,
  Competitor,
  CompetitorCrawlResult,
  DataSufficiency,
  DiscoveryRunResponse,
  DiscoveryStatus,
  HealthStatus,
  MarketInsight,
  OpportunityDraft,
  OpportunityItem,
  PosterPromptResponse,
  PosterRenderResponse,
  ProfileCompleteness,
  WeaknessItem,
} from "../types";

const API_BASE = "/api/v1";

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function fetchCompetitors(params?: {
  city?: string;
  sortBy?: string;
  hasAds?: boolean;
  dataStatus?: string;
}): Promise<Competitor[]> {
  const query = new URLSearchParams();
  if (params?.city) query.set("city", params.city);
  if (params?.sortBy) query.set("sort_by", params.sortBy);
  if (params?.hasAds !== undefined) query.set("has_ads", String(params.hasAds));
  if (params?.dataStatus) query.set("data_status", params.dataStatus);

  const res = await fetch(`${API_BASE}/competitors?${query.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch competitors");
  return res.json();
}

export async function fetchCompetitor(id: number): Promise<Competitor> {
  const res = await fetch(`${API_BASE}/competitors/${id}`);
  if (!res.ok) throw new Error("Failed to fetch competitor details");
  return res.json();
}

export async function addCompetitor(payload: {
  name: string;
  course?: string;
  city?: string;
  fb_page_url?: string;
}): Promise<Competitor> {
  const res = await fetch(`${API_BASE}/competitors`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to add competitor");
  return res.json();
}

export async function resolveCompetitorPage(inputText: string): Promise<{
  resolved_name: string;
  resolved_page_id: string;
  confidence: string;
}> {
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

// Phase A: Profile APIs
export async function fetchProfile(): Promise<BusinessProfile> {
  const res = await fetch(`${API_BASE}/profile`);
  if (!res.ok) throw new Error("Failed to fetch business profile");
  return res.json();
}

export async function updateProfile(payload: Partial<BusinessProfile>): Promise<BusinessProfile> {
  const res = await fetch(`${API_BASE}/profile`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to update profile");
  return res.json();
}

export async function fetchProfileCompleteness(): Promise<ProfileCompleteness> {
  const res = await fetch(`${API_BASE}/profile/completeness`);
  if (!res.ok) throw new Error("Failed to fetch completeness status");
  return res.json();
}

export async function autofillProfile(websiteUrl: string) {
  const res = await fetch(`${API_BASE}/profile/autofill`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ website_url: websiteUrl }),
  });
  if (!res.ok) throw new Error("Failed to autofill from website");
  return res.json();
}

// Phase B: Discovery APIs
export async function startDiscovery(payload?: {
  radius_km?: number;
  city?: string;
  areas?: string[];
  domains?: string[];
  search_terms?: string[];
}): Promise<DiscoveryRunResponse> {
  const res = await fetch(`${API_BASE}/discovery/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || { radius_km: 10.0 }),
  });
  if (!res.ok) throw new Error("Failed to start discovery run");
  return res.json();
}

export async function crawlCompetitorWebsite(websiteUrl: string): Promise<CompetitorCrawlResult> {
  const res = await fetch(`${API_BASE}/competitors/crawl-website`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ website_url: websiteUrl }),
  });
  if (!res.ok) throw new Error("Failed to crawl competitor website");
  return res.json();
}

export async function fetchDiscoveryStatus(runId: number): Promise<DiscoveryStatus> {
  const res = await fetch(`${API_BASE}/discovery/${runId}/status`);
  if (!res.ok) throw new Error("Failed to fetch discovery status");
  return res.json();
}

// Phase D & E: Evidence & Weakness APIs
export async function fetchCompetitorWeaknesses(competitorId: number): Promise<{
  competitor_id: number;
  weaknesses: WeaknessItem[];
  data_status: string;
  total_evidence: number;
  is_sufficient: boolean;
}> {
  const res = await fetch(`${API_BASE}/competitors/${competitorId}/weaknesses`);
  if (!res.ok) throw new Error("Failed to fetch competitor weaknesses");
  return res.json();
}

export async function fetchCompetitorSufficiency(competitorId: number): Promise<DataSufficiency> {
  const res = await fetch(`${API_BASE}/competitors/${competitorId}/sufficiency`);
  if (!res.ok) throw new Error("Failed to fetch data sufficiency");
  return res.json();
}

export async function analyzeCompetitorWeaknesses(competitorId: number): Promise<WeaknessItem[]> {
  const res = await fetch(`${API_BASE}/competitors/${competitorId}/analyze`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail?.message || "Sufficiency requirements not met for analysis");
  }
  return res.json();
}

export async function importEvidence(payload: {
  competitor_id: number;
  source: string;
  text: string;
  category?: string;
}) {
  const res = await fetch(`${API_BASE}/evidence/import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to import evidence");
  return res.json();
}

// Phase F: Opportunity APIs
export async function fetchOpportunities(): Promise<OpportunityItem[]> {
  const res = await fetch(`${API_BASE}/opportunities`);
  if (!res.ok) throw new Error("Failed to fetch opportunities");
  return res.json();
}

export async function draftOpportunityAd(opportunityId: number): Promise<OpportunityDraft> {
  const res = await fetch(`${API_BASE}/opportunities/draft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ opportunity_id: opportunityId }),
  });
  if (!res.ok) throw new Error("Failed to draft counter ad");
  return res.json();
}
