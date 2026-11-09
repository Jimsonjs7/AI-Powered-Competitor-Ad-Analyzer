export interface Competitor {
  id: number;
  name: string;
  city: string;
  course: string;
  website: string | null;
  fb_page_id: string | null;
  confidence: "high" | "medium" | "low" | "needs_review";
  active_ads_count: number;
  is_active: boolean;
  created_at: string;
}

export interface Ad {
  id: number;
  ad_archive_id: string;
  competitor_id: number;
  competitor_name: string;
  course: string;
  copy: string;
  headline: string | null;
  cta: string | null;
  platforms: string[];
  start_date: string | null;
  is_active: boolean;
  first_seen: string;
  last_seen: string;
  run_days: number;
  media_url: string | null;
  media_type: string | null;
  score: number | null;
  hook: string | null;
  offer: string | null;
  audience: string | null;
  tactics: string[];
  why: string | null;
  weak: string | null;
  created_at: string;
}

export interface PosterPromptResponse {
  ad_id: number;
  course: string;
  angle_name: string;
  headline: string;
  subline: string;
  cta_text: string;
  prompt: string;
  size_format: string;
}

export interface PosterRenderResponse {
  poster_id: number;
  headline: string;
  subline: string;
  cta_text: string;
  image_url: string;
  size_format: string;
  status: string;
}

export interface HealthStatus {
  status: string;
  active_providers_count: number;
  total_providers_count: number;
  message: string;
  providers_health: Record<string, { ok: boolean; last_run: string | null }>;
}
