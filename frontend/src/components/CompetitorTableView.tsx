import React, { useState } from "react";
import {
  analyzeCompetitorWeaknesses,
  fetchAds,
  fetchCompetitorWeaknesses,
  importEvidence,
} from "../api/client";
import { Ad, Competitor, WeaknessItem } from "../types";
import { CreativeRecommenderModal } from "./CreativeRecommenderModal";

interface CompetitorTableViewProps {
  competitors: Competitor[];
  onBack: () => void;
  onRefreshCompetitors: () => void;
}

export const CompetitorTableView: React.FC<CompetitorTableViewProps> = ({
  competitors,
  onBack,
  onRefreshCompetitors,
}) => {
  const [selectedCompId, setSelectedCompId] = useState<number | null>(null);
  const [selectedReportAd, setSelectedReportAd] = useState<Ad | null>(null);
  const [detailTab, setDetailTab] = useState<"ads" | "weaknesses">("ads");
  const [competitorAds, setCompetitorAds] = useState<Ad[]>([]);
  const [isLoadingAds, setIsLoadingAds] = useState(false);
  const [counterAdId, setCounterAdId] = useState<number | null>(null);
  const [counterMediaUrl, setCounterMediaUrl] = useState<string | null>(null);
  const [weaknesses, setWeaknesses] = useState<WeaknessItem[]>([]);
  const [isLoadingWeakness, setIsLoadingWeakness] = useState(false);
  const [weaknessError, setWeaknessError] = useState("");

  // Evidence import modal state
  const [evidenceCompId, setEvidenceCompId] = useState<number | null>(null);
  const [evidenceSource, setEvidenceSource] = useState("google_maps");
  const [evidenceText, setEvidenceText] = useState("");
  const [evidenceCategory, setEvidenceCategory] = useState("pricing_clarity");
  const [isImporting, setIsImporting] = useState(false);
  const [evidenceMsg, setEvidenceMsg] = useState("");

  // Filter state
  const [filterCourse, setFilterCourse] = useState("All");
  const [filterHasAds, setFilterHasAds] = useState<"all" | "yes" | "no">("all");
  const [sortBy, setSortBy] = useState<"ads" | "distance" | "name">("ads");

  const handleInspectCompetitor = async (comp: Competitor, tab: "ads" | "weaknesses" = "ads") => {
    setSelectedCompId(comp.id);
    setDetailTab(tab);
    setIsLoadingAds(true);
    setIsLoadingWeakness(true);
    setWeaknessError("");

    try {
      const ads = await fetchAds({ competitorIds: [comp.id] });
      setCompetitorAds(ads);
    } catch {
      setCompetitorAds([]);
    } finally {
      setIsLoadingAds(false);
    }

    try {
      const res = await fetchCompetitorWeaknesses(comp.id);
      if (res.weaknesses.length === 0 && res.is_sufficient) {
        const analyzed = await analyzeCompetitorWeaknesses(comp.id);
        setWeaknesses(analyzed);
      } else {
        setWeaknesses(res.weaknesses);
      }
    } catch (err: any) {
      setWeaknessError(err.message || "Failed to load weaknesses");
    } finally {
      setIsLoadingWeakness(false);
    }
  };

  const handleImportEvidence = async () => {
    if (!evidenceCompId || !evidenceText.trim()) return;
    setIsImporting(true);
    setEvidenceMsg("");
    try {
      await importEvidence({
        competitor_id: evidenceCompId,
        source: evidenceSource,
        text: evidenceText.trim(),
        category: evidenceCategory,
      });
      setEvidenceMsg("Evidence imported and sanitized.");
      setEvidenceText("");
      setTimeout(() => {
        setEvidenceCompId(null);
        setEvidenceMsg("");
        onRefreshCompetitors();
      }, 1000);
    } catch (err) {
      setEvidenceMsg("Failed to import evidence.");
    } finally {
      setIsImporting(false);
    }
  };

  // Filter & sort
  let filtered = [...competitors];
  if (filterCourse !== "All") {
    filtered = filtered.filter((c) => c.course === filterCourse);
  }
  if (filterHasAds === "yes") {
    filtered = filtered.filter((c) => c.active_ads_count > 0);
  } else if (filterHasAds === "no") {
    filtered = filtered.filter((c) => c.active_ads_count === 0);
  }

  if (sortBy === "ads") {
    filtered.sort((a, b) => b.active_ads_count - a.active_ads_count);
  } else if (sortBy === "distance") {
    filtered.sort((a, b) => (a.distance_km || 99) - (b.distance_km || 99));
  } else if (sortBy === "name") {
    filtered.sort((a, b) => a.name.localeCompare(b.name));
  }

  const selectedComp = competitors.find((c) => c.id === selectedCompId);

  return (
    <div style={{ maxWidth: 1140, margin: "0 auto", padding: "24px 20px", display: "flex", flexDirection: "column", gap: 18 }}>
      {/* Top Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 18 }}>Competitor Directory & Data Sufficiency</h2>
          <p style={{ margin: "4px 0 0", color: "var(--muted)", fontSize: 13 }}>
            Inspect competitor metrics, distance, active ad volume, and live ad intelligence.
          </p>
        </div>
        <button className="btn" onClick={onBack}>
          Back to ad wall
        </button>
      </div>

      {/* Filter and Sort Controls */}
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center", background: "var(--surface)", padding: "10px 14px", border: "1px solid var(--line)", borderRadius: 6 }}>
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <label style={{ fontSize: 12, fontWeight: 600 }}>Course:</label>
          {["All", "AI", "Digital marketing", "UI/UX"].map((c) => (
            <button
              key={c}
              className="fl"
              aria-pressed={filterCourse === c}
              onClick={() => setFilterCourse(c)}
              style={{ fontSize: 12, padding: "4px 8px" }}
            >
              {c}
            </button>
          ))}
        </div>

        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <label style={{ fontSize: 12, fontWeight: 600 }}>Active Ads:</label>
          <select
            value={filterHasAds}
            onChange={(e: any) => setFilterHasAds(e.target.value)}
            style={{ fontSize: 13, padding: "3px 6px" }}
          >
            <option value="all">All</option>
            <option value="yes">With active ads</option>
            <option value="no">Zero ads</option>
          </select>
        </div>

        <div style={{ display: "flex", gap: 6, alignItems: "center", marginLeft: "auto" }}>
          <label style={{ fontSize: 12, fontWeight: 600 }}>Sort by:</label>
          <select
            value={sortBy}
            onChange={(e: any) => setSortBy(e.target.value)}
            style={{ fontSize: 13, padding: "3px 6px" }}
          >
            <option value="ads">Most active ads</option>
            <option value="distance">Nearest first</option>
            <option value="name">Alphabetical</option>
          </select>
        </div>
      </div>

      {/* Competitors Table */}
      <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: 14 }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--line)", background: "var(--canvas)", color: "var(--muted)", fontSize: 12, textTransform: "uppercase" }}>
              <th style={{ padding: "10px 14px" }}>Competitor</th>
              <th style={{ padding: "10px 14px" }}>Course</th>
              <th style={{ padding: "10px 14px" }}>Location</th>
              <th style={{ padding: "10px 14px" }}>Active Ads</th>
              <th style={{ padding: "10px 14px" }}>Data Status</th>
              <th style={{ padding: "10px 14px", textAlign: "right" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              competitors.length === 0 ? (
                // Skeleton loading rows
                [1, 2, 3, 4, 5].map((idx) => (
                  <tr key={idx} style={{ borderBottom: "1px solid var(--line)" }}>
                    <td style={{ padding: "12px 14px" }}>
                      <div className="skeleton" style={{ width: 140, height: 16 }} />
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <div className="skeleton" style={{ width: 80, height: 16 }} />
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <div className="skeleton" style={{ width: 120, height: 16 }} />
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <div className="skeleton" style={{ width: 60, height: 16 }} />
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <div className="skeleton" style={{ width: 90, height: 22, borderRadius: 12 }} />
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "right" }}>
                      <div className="skeleton" style={{ width: 100, height: 26, marginLeft: "auto", borderRadius: 4 }} />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} style={{ padding: "28px 14px", textAlign: "center", color: "var(--muted)" }}>
                    No competitors match the selected filters.
                  </td>
                </tr>
              )
            ) : (
              filtered.map((comp) => {
                return (
                  <tr key={comp.id} style={{ borderBottom: "1px solid var(--line)" }}>
                    <td style={{ padding: "12px 14px", fontWeight: 600 }}>
                      <a
                        href="#inspect"
                        onClick={(e) => {
                          e.preventDefault();
                          handleInspectCompetitor(comp, "ads");
                        }}
                        style={{ color: "var(--ink)", textDecoration: "none", borderBottom: "1px dashed var(--line)" }}
                      >
                        {comp.name}
                      </a>
                    </td>
                    <td style={{ padding: "12px 14px" }}>{comp.course}</td>
                    <td style={{ padding: "12px 14px", color: "var(--muted)" }}>
                      {comp.city} {comp.area ? `· ${comp.area}` : ""} {comp.distance_km ? `(${comp.distance_km} km)` : ""}
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <b>{comp.active_ads_count}</b> ads
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      {comp.data_status === "analyzed" ? (
                        <span
                          className="chip"
                          style={{
                            background: "#ecfdf5",
                            color: "#065f46",
                            fontWeight: 600,
                          }}
                        >
                          Analyzed
                        </span>
                      ) : comp.active_ads_count > 0 ? (
                        <span
                          className="chip"
                          style={{
                            background: "var(--accent-soft)",
                            color: "var(--accent)",
                            fontWeight: 600,
                          }}
                        >
                          {comp.active_ads_count} {comp.active_ads_count === 1 ? "ad" : "ads"} tracked
                        </span>
                      ) : (
                        <span
                          className="chip"
                          style={{
                            background: "var(--canvas)",
                            color: "var(--muted)",
                          }}
                        >
                          Zero active ads
                        </span>
                      )}
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "right" }}>
                      <div style={{ display: "inline-flex", gap: 6 }}>
                      <button
                        className="btn"
                        style={{ fontSize: 12, padding: "3px 8px" }}
                        onClick={() => handleInspectCompetitor(comp, "ads")}
                      >
                        Inspect & Ads
                      </button>
                      <button
                        className="btn"
                        style={{ fontSize: 12, padding: "3px 8px" }}
                        onClick={() => setEvidenceCompId(comp.id)}
                      >
                        Add Evidence
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })
          )}
          </tbody>
        </table>
      </div>

      {/* Competitor Comprehensive Details Panel */}
      {selectedComp && (
        <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, padding: 20 }}>
          {/* Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                <h3 style={{ margin: 0, fontSize: 17 }}>{selectedComp.name}</h3>
                <span className="chip" style={{ background: "var(--accent-soft)", color: "var(--accent)" }}>
                  {selectedComp.course}
                </span>
                <span className="chip" style={{ background: "var(--canvas)", color: "var(--muted)" }}>
                  {selectedComp.city} {selectedComp.area ? `· ${selectedComp.area}` : ""}
                </span>
              </div>
              <div style={{ fontSize: 12, color: "var(--muted)", display: "flex", gap: 12 }}>
                {selectedComp.website && (
                  <a href={selectedComp.website} target="_blank" rel="noreferrer" style={{ color: "var(--accent)" }}>
                    Website
                  </a>
                )}
                {selectedComp.fb_page_id && (
                  <span>Meta Page ID: <code>{selectedComp.fb_page_id}</code></span>
                )}
                {selectedComp.ig_handle && (
                  <span>Instagram: @{selectedComp.ig_handle}</span>
                )}
              </div>
            </div>
            <button className="btn" onClick={() => setSelectedCompId(null)}>
              Close
            </button>
          </div>

          {/* Tab selector */}
          <div style={{ display: "flex", gap: 8, borderBottom: "1px solid var(--line)", paddingBottom: 10, marginBottom: 16 }}>
            <button
              className="fl"
              aria-pressed={detailTab === "ads"}
              onClick={() => setDetailTab("ads")}
              style={{ fontSize: 13, padding: "5px 12px" }}
            >
              Active Running Ads ({competitorAds.length})
            </button>
            <button
              className="fl"
              aria-pressed={detailTab === "weaknesses"}
              onClick={() => setDetailTab("weaknesses")}
              style={{ fontSize: 13, padding: "5px 12px" }}
            >
              Weakness Analysis ({weaknesses.length})
            </button>
          </div>

          {/* Tab 1: Running Ads */}
          {detailTab === "ads" && (
            <div>
              {isLoadingAds ? (
                <p style={{ color: "var(--muted)", fontSize: 13 }}>Loading active running ads...</p>
              ) : competitorAds.length === 0 ? (
                <div style={{ padding: 18, background: "var(--canvas)", borderRadius: 6, fontSize: 13, color: "var(--muted)" }}>
                  No active ads collected for this competitor yet. Click <b>Refresh ads</b> in the top bar to fetch from Meta Ad Library, or add a Meta Ad Library URL.
                </div>
              ) : (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 14 }}>
                  {competitorAds.map((ad) => (
                    <div
                      key={ad.id}
                      style={{
                        background: "var(--canvas)",
                        border: "1px solid var(--line)",
                        borderRadius: 6,
                        overflow: "hidden",
                        display: "flex",
                        flexDirection: "column",
                      }}
                    >
                      {ad.media_url ? (
                        <img
                          src={ad.media_url}
                          alt="Creative preview"
                          style={{ width: "100%", height: 160, objectFit: "cover" }}
                        />
                      ) : (
                        <div
                          style={{
                            height: 100,
                            background: "var(--surface)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "var(--muted)",
                            fontSize: 12,
                          }}
                        >
                          Ad Creative Card
                        </div>
                      )}
                      <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 8, flex: 1 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <span className="chip" style={{ fontSize: 11, background: "var(--accent-soft)", color: "var(--accent)" }}>
                            Running for {ad.run_days} days
                          </span>
                          {ad.cta && (
                            <span style={{ fontSize: 11, color: "var(--muted)", fontWeight: 500 }}>
                              CTA: {ad.cta}
                            </span>
                          )}
                        </div>

                        {ad.headline && (
                          <div style={{ fontWeight: 600, fontSize: 13 }}>{ad.headline}</div>
                        )}

                        <div
                          style={{
                            fontSize: 12,
                            color: "var(--ink)",
                            lineHeight: 1.4,
                            maxHeight: 70,
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                          }}
                        >
                          {ad.copy}
                        </div>

                        <div style={{ marginTop: "auto", borderTop: "1px solid var(--line)", paddingTop: 8, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <span style={{ fontSize: 11, color: "var(--muted)", maxWidth: "60%", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            {ad.hook ? `Hook: ${ad.hook}` : "Active Ad"}
                          </span>
                          <div style={{ display: "inline-flex", gap: 6 }}>
                            <button
                              className="btn"
                              onClick={() => setSelectedReportAd(ad)}
                              style={{ fontSize: 11, padding: "3px 8px" }}
                            >
                              Marketing Report
                            </button>
                            <button
                              className="btn pri"
                              onClick={() => {
                                setCounterAdId(ad.id);
                                setCounterMediaUrl(ad.media_url);
                              }}
                              style={{ fontSize: 11, padding: "3px 8px" }}
                            >
                              Counter this Ad
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Weaknesses */}
          {detailTab === "weaknesses" && (
            <div>
              {isLoadingWeakness ? (
                <p style={{ color: "var(--muted)", fontSize: 13 }}>Checking data sufficiency and analyzing evidence...</p>
              ) : weaknessError ? (
                <div style={{ padding: 10, background: "var(--warn-soft)", borderRadius: 6, color: "var(--warn)", fontSize: 13 }}>
                  {weaknessError}
                </div>
              ) : weaknesses.length === 0 ? (
                <p style={{ color: "var(--muted)", fontSize: 13 }}>
                  No weaknesses analyzed yet. Collect more ads or add public customer review evidence.
                </p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {weaknesses.map((w) => (
                    <div key={w.id} style={{ padding: "10px 12px", border: "1px solid var(--line)", borderRadius: 6 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                        <b>{w.category.replace("_", " ").toUpperCase()}</b>
                        <span style={{ fontSize: 12, color: "var(--muted)" }}>
                          Severity {w.severity}/5 | {w.evidence_count} evidence items ({w.share_percent}%) | Confidence: {w.confidence}
                        </span>
                      </div>
                      <div style={{ fontSize: 14 }}>{w.summary}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Add Evidence Modal */}
      {evidenceCompId && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 20,
            zIndex: 100,
          }}
        >
          <div
            style={{
              background: "var(--surface)",
              borderRadius: 8,
              maxWidth: 500,
              width: "100%",
              padding: 20,
              display: "flex",
              flexDirection: "column",
              gap: 14,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ margin: 0, fontSize: 16 }}>Import Customer Review or Public Comment</h3>
              <button className="btn" onClick={() => setEvidenceCompId(null)}>
                Cancel
              </button>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 4 }}>Source</label>
              <select
                value={evidenceSource}
                onChange={(e) => setEvidenceSource(e.target.value)}
                style={{ width: "100%", padding: "6px 8px", border: "1px solid var(--line)", borderRadius: 6 }}
              >
                <option value="google_maps">Google Maps Review</option>
                <option value="fb_comments">Facebook Public Comment</option>
                <option value="manual">Manual Student Note / Screenshot</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 4 }}>Doubt / Concern Category</label>
              <select
                value={evidenceCategory}
                onChange={(e) => setEvidenceCategory(e.target.value)}
                style={{ width: "100%", padding: "6px 8px", border: "1px solid var(--line)", borderRadius: 6 }}
              >
                <option value="pricing_clarity">Pricing clarity & hidden fees</option>
                <option value="placement_claims">Placement & hiring partner claims</option>
                <option value="schedule_clarity">Schedule & batch timing clarity</option>
                <option value="trust_proof">Mentor credentials & trust proof</option>
                <option value="teaching_quality">Teaching quality & project depth</option>
                <option value="student_support">Student support & response time</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 4 }}>
                Review / Comment Text (User names will be automatically stripped)
              </label>
              <textarea
                rows={4}
                placeholder="e.g. They asked for ₹5000 extra for certification. No placement help provided."
                value={evidenceText}
                onChange={(e) => setEvidenceText(e.target.value)}
                style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
              />
            </div>

            {evidenceMsg && <div style={{ fontSize: 13, color: "var(--accent)" }}>{evidenceMsg}</div>}

            <button className="btn pri" disabled={isImporting || !evidenceText.trim()} onClick={handleImportEvidence}>
              {isImporting ? "Saving..." : "Save Evidence"}
            </button>
          </div>
        </div>
      )}

      {/* Competitor Marketing Report Modal */}
      {selectedReportAd && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.45)",
            zIndex: 1000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 20,
          }}
          onClick={() => setSelectedReportAd(null)}
        >
          <div
            style={{
              background: "var(--surface)",
              borderRadius: 8,
              border: "1px solid var(--line)",
              width: "100%",
              maxWidth: 620,
              maxHeight: "90vh",
              overflowY: "auto",
              padding: 24,
              display: "flex",
              flexDirection: "column",
              gap: 16,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                  <span className="chip" style={{ background: "var(--accent-soft)", color: "var(--accent)", fontWeight: 600 }}>
                    Marketing Intelligence Report
                  </span>
                  <span className="chip" style={{ background: "var(--canvas)", color: "var(--muted)" }}>
                    {selectedReportAd.platforms?.join(" / ") || "Meta"}
                  </span>
                </div>
                <h3 style={{ margin: 0, fontSize: 18 }}>{selectedReportAd.competitor_name}</h3>
                <p style={{ margin: "2px 0 0", color: "var(--muted)", fontSize: 13 }}>
                  {selectedReportAd.course} · Running for {selectedReportAd.run_days} days
                </p>
              </div>
              <button className="btn" onClick={() => setSelectedReportAd(null)}>
                Close
              </button>
            </div>

            {/* Target Audience Persona Card */}
            <div style={{ background: "var(--canvas)", border: "1px solid var(--line)", borderRadius: 6, padding: 14 }}>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", marginBottom: 8 }}>
                Target audience profile & intent
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 13, lineHeight: 1.45 }}>
                <div>
                  <strong style={{ color: "var(--ink)" }}>Primary Persona:</strong>{" "}
                  <span style={{ color: "var(--muted)" }}>{selectedReportAd.audience || "Fresh college graduates and non-technical professionals seeking job transitions (Ages 20-28)"}</span>
                </div>
                <div>
                  <strong style={{ color: "var(--ink)" }}>Psychological Mindset:</strong>{" "}
                  <span style={{ color: "var(--muted)" }}>
                    Anxious about hiring freezes and career stagnation. Looking for fast reassurance, guaranteed outcomes, and peer validation.
                  </span>
                </div>
                <div>
                  <strong style={{ color: "var(--ink)" }}>Ad Funnel Stage:</strong>{" "}
                  <span style={{ color: "var(--muted)" }}>
                    {selectedReportAd.run_days > 25
                      ? "High-intent middle/bottom funnel (converting active seekers comparing institutes)"
                      : "Top-of-funnel impression driver (generating initial curiosity and contact leads)"}
                  </span>
                </div>
              </div>
            </div>

            {/* What They Really Mean Card */}
            <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderLeft: "4px solid #0a7c6e", borderRadius: 6, padding: 14 }}>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", marginBottom: 8 }}>
                Decoded ad subtext (what they really mean)
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 10, fontSize: 13, lineHeight: 1.5 }}>
                <div style={{ background: "var(--canvas)", padding: "8px 10px", borderRadius: 4, border: "1px solid var(--line)" }}>
                  <span style={{ fontSize: 11, color: "var(--muted)", display: "block", fontWeight: 600 }}>SURFACE MARKETING PITCH:</span>
                  <span style={{ color: "var(--ink)", fontWeight: 600 }}>"{selectedReportAd.hook || selectedReportAd.headline || selectedReportAd.offer || 'Enroll now for fast career launch'}"</span>
                </div>
                <div>
                  <span style={{ fontSize: 11, color: "#0a7c6e", display: "block", fontWeight: 700 }}>THE REALITY BEHIND THE PITCH:</span>
                  <p style={{ margin: "2px 0 0", color: "var(--ink)" }}>
                    {selectedReportAd.why || "The competitor uses a blanket outcome promise to capture contact details quickly, hiding curriculum rigor and batch fee schedules behind a phone sales wall."}
                  </p>
                </div>
                <div style={{ borderTop: "1px solid var(--line)", paddingTop: 8 }}>
                  <span style={{ fontSize: 11, color: "var(--warn)", display: "block", fontWeight: 700 }}>COMPETITOR VULNERABILITY:</span>
                  <p style={{ margin: "2px 0 0", color: "var(--ink)" }}>
                    {selectedReportAd.weak || "Omission of transparent batch fees, verified alumni portfolio links, and real hiring partner proof."}
                  </p>
                </div>
              </div>
            </div>

            {/* Marketing Team Action Battlecard */}
            <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 6, padding: 14 }}>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", marginBottom: 10 }}>
                BrandMonk team battlecard & counter-play
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 10, fontSize: 13, lineHeight: 1.45 }}>
                <div>
                  <strong style={{ color: "var(--accent)" }}>Ad Campaign Strategy:</strong>
                  <p style={{ margin: "2px 0 0", color: "var(--ink)" }}>
                    Run a proof-contrast counter ad. While {selectedReportAd.competitor_name} emphasizes broad claims, BrandMonk should highlight upfront syllabus transparency and mentor portfolio reviews.
                  </p>
                </div>
                <div style={{ borderTop: "1px dashed var(--line)", paddingTop: 8 }}>
                  <strong style={{ color: "var(--ink)" }}>Admissions Counselor Talking Point:</strong>
                  <p style={{ margin: "2px 0 0", color: "var(--muted)", fontStyle: "italic" }}>
                    "When prospects bring up {selectedReportAd.competitor_name}'s promises, ask them if they were shown actual week-by-week live projects or if it's mostly self-paced videos. At BrandMonk, working practitioners review your code live."
                  </p>
                </div>
              </div>
            </div>

            <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
              <button
                className="btn pri"
                style={{ flex: 1 }}
                onClick={() => {
                  setCounterAdId(selectedReportAd.id);
                  setCounterMediaUrl(selectedReportAd.media_url);
                  setSelectedReportAd(null);
                }}
              >
                Generate Counter-Ad Strategy
              </button>
              <button className="btn" onClick={() => setSelectedReportAd(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Strategic Creative Counter-Ad Recommender Modal */}
      <CreativeRecommenderModal
        adId={counterAdId}
        isOpen={!!counterAdId}
        onClose={() => setCounterAdId(null)}
        competitorMediaUrl={counterMediaUrl}
      />
    </div>
  );
};

