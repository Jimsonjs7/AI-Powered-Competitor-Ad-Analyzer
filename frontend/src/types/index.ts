export interface CompetitorMetrics {
  active_ads: number;
  new_this_week: number;
  longest_run_days: number;
  rating: number | null;
  review_count: number;
  negative_share: number;
  comment_count: number;
  weakness_score: number;
  threat_score: number;
  computed_at: string | null;
}

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
  lat?: number | null;
  lng?: number | null;
  distance_km?: number | null;
  area?: string | null;
  ig_handle?: string | null;
  data_status: "pending" | "has_ads" | "ready" | "analyzed";
  metrics?: CompetitorMetrics | null;
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

export interface MarketInsight {
  headline: string;
  subline: string;
  top_hook: string;
  hook_percentage: number;
  course_distribution: Record<string, number>;
  gap_course: string;
  total_active_ads: number;
}

// Phase A: Profile Types
export interface ProfileServiceItem {
  id?: number;
  name: string;
  description?: string;
  fee_min?: number;
  fee_max?: number;
  duration?: string;
  mode?: string;
  next_batch?: string;
  outcomes?: string;
}

export interface ProfileClaimItem {
  id?: number;
  text: string;
  proof_link?: string;
  approved: boolean;
}

export interface ProfileSocialItem {
  id?: number;
  platform: string;
  url_or_handle: string;
  verified?: boolean;
}

export interface BusinessProfile {
  id: number;
  version: number;
  name: string;
  description?: string;
  tagline?: string;
  business_type: string[];
  domains: string[];
  city: string;
  area?: string;
  lat?: number;
  lng?: number;
  radius_km: number;
  website?: string;
  tone: string;
  target_audience?: string;
  price_positioning: string;
  languages: string[];
  primary_goal: string;
  monthly_budget_range?: string;
  preferred_cta: string;
  thresholds: {
    min_ads: number;
    min_reviews: number;
    min_comments: number;
  };
  services: ProfileServiceItem[];
  claims: ProfileClaimItem[];
  social_accounts: ProfileSocialItem[];
}

export interface ProfileCompleteness {
  score: number;
  missing_fields: Array<{ field: string; hint: string; impact: string }>;
  is_ready_for_discovery: boolean;
}

// Phase B: Discovery Types
export interface DiscoveryRunResponse {
  run_id: number;
  status: string;
  message: string;
}

export interface DiscoveryStatus {
  run_id: number;
  status: string;
  current_step?: string;
  radius_km: number;
  counts: Record<string, number>;
  started_at: string;
  finished_at?: string;
}

export interface CompetitorCrawlResult {
  name: string;
  course: string;
  city: string;
  area?: string;
  website: string;
  fb_page_id?: string;
  fb_url?: string;
  ig_handle?: string;
  description?: string;
  detected_social_links: string[];
}

// Phase D & E: Evidence and Weakness Types
export interface WeaknessItem {
  id: number;
  competitor_id: number;
  category: string;
  summary: string;
  evidence_count: number;
  sample_size: number;
  share_percent: number;
  confidence: "high" | "medium" | "low";
  severity: number;
  computed_at: string;
}

export interface DataSufficiency {
  competitor_id: number;
  ads_count: number;
  reviews_count: number;
  comments_count: number;
  is_sufficient: boolean;
  missing: string[];
}

// Phase F: Opportunity Types
export interface OpportunityItem {
  id: number;
  cluster_id: number;
  cluster_label: string;
  category: string;
  score: number;
  counter_angle?: string;
  formats: string[];
  headlines: string[];
  primary_text?: string;
  missing_proof: string[];
  status: string;
}

export interface OpportunityDraft {
  opportunity_id: number;
  headline_options: string[];
  primary_text: string;
  cta: string;
  recommended_format: string;
  used_claims: string[];
  missing_claims: string[];
  compliance_note: string;
}

// Creative Ads Recommender
export interface CompetitorAdFlawAudit {
  competitor_name: string;
  headline?: string;
  copy_snippet: string;
  active_days: number;
  detected_hook: string;
  detected_offer: string;
  vulnerabilities: string[];
  creative_fatigue_level: string;
  unaddressed_prospect_doubts: string[];
}

export interface CounterCreativeAngle {
  angle_type: "contrarian" | "proof_roi" | "transparency";
  angle_name: string;
  strategic_rationale: string;
  target_flaw_in_competitor: string;
  matching_approved_claim: string;
  hook: string;
  headline: string;
  subline: string;
  primary_text: string;
  cta_text: string;
  urgency_tagline?: string;
  visual_concept: string;
  composition: string;
  color_palette: string[];
  typography_guide: string;
  aspect_ratios: Record<string, string>;
  image_prompt: string;
  negative_prompt: string;
}

export interface CreativeCounterAdResponse {
  ad_id: number;
  client_name: string;
  course: string;
  competitor_audit: CompetitorAdFlawAudit;
  angles: CounterCreativeAngle[];
  recommended_cta: string;
  created_at: string;
}
