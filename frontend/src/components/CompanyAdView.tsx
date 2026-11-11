import React, { useState, useMemo } from "react";
import { Ad, Competitor } from "../types";
import { AdPosterCard } from "./AdPosterCard";
import { CreativeRecommenderModal } from "./CreativeRecommenderModal";

interface CompanyAdViewProps {
  competitors: Competitor[];
  ads: Ad[];
  initialCompanyId?: number | null;
  onBackToWall: () => void;
  onSelectAdForPoster?: (ad: Ad) => void;
}

export const CompanyAdView: React.FC<CompanyAdViewProps> = ({
  competitors,
  ads,
  initialCompanyId = null,
  onBackToWall,
  onSelectAdForPoster,
}) => {
  const [selectedCourse, setSelectedCourse] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedPlatform, setSelectedPlatform] = useState<string>("All");
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(initialCompanyId);
  const [recommenderAdId, setRecommenderAdId] = useState<number | null>(null);
  const [recommenderMediaUrl, setRecommenderMediaUrl] = useState<string | null>(null);

  // Group ads by competitor ID
  const adsByCompetitor = useMemo(() => {
    const map = new Map<number, Ad[]>();
    for (const ad of ads) {
      const list = map.get(ad.competitor_id) || [];
      list.push(ad);
      map.set(ad.competitor_id, list);
    }
    return map;
  }, [ads]);

  // Filter competitors based on course and search
  const filteredCompetitors = useMemo(() => {
    return competitors.filter((comp) => {
      const matchCourse = selectedCourse === "All" || comp.course === selectedCourse;
      const matchSearch =
        !searchQuery.trim() ||
        comp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (comp.area && comp.area.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchCourse && matchSearch;
    });
  }, [competitors, selectedCourse, searchQuery]);

  // Automatically select first competitor with ads if none selected
  const activeSelectedId = useMemo(() => {
    if (selectedCompanyId !== null) return selectedCompanyId;
    const firstWithAds = filteredCompetitors.find((c) => (adsByCompetitor.get(c.id)?.length || 0) > 0);
    return firstWithAds ? firstWithAds.id : filteredCompetitors[0]?.id || null;
  }, [selectedCompanyId, filteredCompetitors, adsByCompetitor]);

  const selectedCompany = useMemo(() => {
    return competitors.find((c) => c.id === activeSelectedId) || null;
  }, [competitors, activeSelectedId]);

  // Ads for the active selected company, filtered by platform
  const companyAds = useMemo(() => {
    if (!activeSelectedId) return [];
    const list = adsByCompetitor.get(activeSelectedId) || [];
    if (selectedPlatform === "All") return list;
    return list.filter((a) =>
      a.platforms.some((p) => p.toLowerCase() === selectedPlatform.toLowerCase())
    );
  }, [activeSelectedId, adsByCompetitor, selectedPlatform]);

  const courses = ["All", "AI", "Digital marketing", "UI/UX"];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 56px)", background: "var(--canvas)" }}>
      {/* Top Filter & Navigation Bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 20px",
          background: "var(--surface)",
          borderBottom: "1px solid var(--line)",
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <button className="btn" onClick={onBackToWall} style={{ fontSize: 13, padding: "5px 10px" }}>
            Back to ad wall
          </button>
          <div style={{ height: 20, width: 1, background: "var(--line)" }} />
          <span style={{ fontWeight: 700, fontSize: 15, color: "var(--ink)" }}>
            Competitor Intelligence Dossier
          </span>
          <span className="chip" style={{ background: "var(--accent-soft)", color: "var(--accent)", fontWeight: 600 }}>
            Categorized by institution
          </span>
        </div>

        {/* Filter Bar */}
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ display: "flex", gap: 4 }}>
            {courses.map((c) => (
              <button
                key={c}
                className="fl"
                aria-pressed={selectedCourse === c}
                onClick={() => setSelectedCourse(c)}
                style={{ fontSize: 12, padding: "4px 9px" }}
              >
                {c === "All" ? "All courses" : c}
              </button>
            ))}
          </div>

          <div style={{ height: 16, width: 1, background: "var(--line)" }} />

          <select
            aria-label="Platform filter"
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            style={{ fontSize: 12, padding: "4px 8px" }}
          >
            <option value="All">All platforms</option>
            <option value="Facebook">Facebook</option>
            <option value="Instagram">Instagram</option>
          </select>
        </div>
      </div>

      {/* Main Two-Column View */}
      <div style={{ display: "flex", flex: 1, minHeight: 0, overflow: "hidden" }}>
        {/* Left Column: Companies Category List */}
        <div
          style={{
            width: 320,
            background: "var(--surface)",
            borderRight: "1px solid var(--line)",
            display: "flex",
            flexDirection: "column",
            flexShrink: 0,
          }}
        >
          {/* Search box */}
          <div style={{ padding: "12px 14px", borderBottom: "1px solid var(--line)" }}>
            <input
              type="text"
              placeholder="Filter institutions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: "100%", fontSize: 13, padding: "6px 10px" }}
            />
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8, fontSize: 11, color: "var(--muted)" }}>
              <span>{filteredCompetitors.length} institutions tracked</span>
              <span>{ads.length} total active ads</span>
            </div>
          </div>

          {/* List of Institutions */}
          <div style={{ flex: 1, overflowY: "auto", padding: "8px" }}>
            {filteredCompetitors.map((comp) => {
              const compAds = adsByCompetitor.get(comp.id) || [];
              const isSelected = comp.id === activeSelectedId;

              return (
                <div
                  key={comp.id}
                  onClick={() => setSelectedCompanyId(comp.id)}
                  style={{
                    padding: "12px 14px",
                    borderRadius: 6,
                    cursor: "pointer",
                    marginBottom: 6,
                    background: isSelected ? "var(--canvas)" : "transparent",
                    border: isSelected ? "1px solid var(--accent)" : "1px solid transparent",
                    transition: "all 0.15s ease",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontWeight: 600, fontSize: 14, color: isSelected ? "var(--accent)" : "var(--ink)" }}>
                      {comp.name}
                    </span>
                    <span
                      className="chip"
                      style={{
                        fontSize: 11,
                        background: compAds.length > 0 ? "var(--accent-soft)" : "var(--canvas)",
                        color: compAds.length > 0 ? "var(--accent)" : "var(--muted)",
                        fontWeight: compAds.length > 0 ? 700 : 500,
                      }}
                    >
                      {compAds.length} {compAds.length === 1 ? "ad" : "ads"}
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "var(--muted)" }}>
                    <span>{comp.course}</span>
                    <span>·</span>
                    <span>{comp.city}</span>
                    {comp.area && <span>({comp.area})</span>}
                  </div>
                </div>
              );
            })}

            {filteredCompetitors.length === 0 && (
              <div style={{ padding: 24, textAlign: "center", color: "var(--muted)", fontSize: 13 }}>
                No institutions match the filter.
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Institution Ads & Strategy Breakdown */}
        <div style={{ flex: 1, overflowY: "auto", padding: "24px 32px" }}>
          {selectedCompany ? (
            <div style={{ maxWidth: 1040, margin: "0 auto", display: "flex", flexDirection: "column", gap: 20 }}>
              {/* Institution Header Card */}
              <div
                style={{
                  background: "var(--surface)",
                  border: "1px solid var(--line)",
                  borderRadius: 8,
                  padding: "20px 24px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  flexWrap: "wrap",
                  gap: 16,
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                    <h2 style={{ margin: 0, fontSize: 20, color: "var(--ink)", letterSpacing: "-0.01em" }}>
                      {selectedCompany.name}
                    </h2>
                    <span className="chip" style={{ background: "var(--accent-soft)", color: "var(--accent)", fontWeight: 600 }}>
                      {selectedCompany.course}
                    </span>
                    <span className="chip" style={{ background: "var(--canvas)", color: "var(--muted)" }}>
                      {selectedCompany.city} {selectedCompany.area ? `· ${selectedCompany.area}` : ""}
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 14, fontSize: 13, color: "var(--muted)", flexWrap: "wrap" }}>
                    {selectedCompany.website && (
                      <a href={selectedCompany.website} target="_blank" rel="noreferrer" style={{ color: "var(--accent)", textDecoration: "none" }}>
                        Website
                      </a>
                    )}
                    {selectedCompany.fb_page_id && (
                      <span>Meta Ad Library Page: <code>{selectedCompany.fb_page_id}</code></span>
                    )}
                    {selectedCompany.ig_handle && (
                      <span>Instagram: @{selectedCompany.ig_handle}</span>
                    )}
                  </div>
                </div>

                <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 18, fontWeight: 700, color: "var(--ink)" }}>
                      {companyAds.length} Active {companyAds.length === 1 ? "Ad" : "Ads"}
                    </div>
                    <div style={{ fontSize: 12, color: "var(--muted)" }}>
                      Running in {selectedCompany.city}
                    </div>
                  </div>
                </div>
              </div>

              {/* Ads List */}
              {companyAds.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <h3 style={{ margin: 0, fontSize: 16, color: "var(--ink)" }}>
                      Active Meta Ad Creatives & Intelligence Breakdown
                    </h3>
                    <span style={{ fontSize: 12, color: "var(--muted)" }}>
                      Showing {companyAds.length} of {companyAds.length} ads
                    </span>
                  </div>

                  {companyAds.map((ad) => {
                    return (
                      <div
                        key={ad.id}
                        style={{
                          background: "var(--surface)",
                          border: "1px solid var(--line)",
                          borderRadius: 8,
                          padding: 20,
                          display: "grid",
                          gridTemplateColumns: "240px 1fr",
                          gap: 24,
                        }}
                      >
                        {/* Left Side: Media Preview & Actions */}
                        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                          <AdPosterCard ad={ad} />

                          <div style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 12 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", color: "var(--muted)" }}>
                              <span>Longevity:</span>
                              <strong style={{ color: "var(--ink)" }}>{ad.run_days} days active</strong>
                            </div>
                            <div style={{ display: "flex", justifyContent: "space-between", color: "var(--muted)" }}>
                              <span>Platforms:</span>
                              <strong style={{ color: "var(--ink)" }}>{ad.platforms.join(", ")}</strong>
                            </div>
                            {ad.start_date && (
                              <div style={{ display: "flex", justifyContent: "space-between", color: "var(--muted)" }}>
                                <span>First seen:</span>
                                <span>{ad.start_date}</span>
                              </div>
                            )}
                          </div>

                          {ad.media_url && (
                            <a
                              href={ad.media_url}
                              target="_blank"
                              rel="noreferrer"
                              className="btn"
                              style={{ fontSize: 12, padding: "5px 8px", textAlign: "center", textDecoration: "none" }}
                            >
                              {ad.media_type === "video" ? "Watch video creative" : "View original ad image"}
                            </a>
                          )}

                          <button
                            className="btn pri"
                            style={{ fontSize: 12, padding: "7px 10px", marginTop: 4 }}
                            onClick={() => {
                              setRecommenderAdId(ad.id);
                              setRecommenderMediaUrl(ad.media_url);
                            }}
                          >
                            Launch counter-ad
                          </button>

                          {onSelectAdForPoster && (
                            <button
                              className="btn"
                              style={{ fontSize: 12, padding: "6px 10px" }}
                              onClick={() => onSelectAdForPoster(ad)}
                            >
                              Generate BrandMonk poster
                            </button>
                          )}
                        </div>

                        {/* Right Side: Detailed Intelligence & Attractive Explanation */}
                        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                          {/* Top Headline & Score */}
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
                            <div>
                              <span className="chip" style={{ background: "var(--accent-soft)", color: "var(--accent)", fontWeight: 600, marginBottom: 4, display: "inline-block" }}>
                                {ad.course} Course Ad
                              </span>
                              <h4 style={{ margin: "2px 0 4px", fontSize: 16, color: "var(--ink)" }}>
                                "{ad.headline || ad.copy.slice(0, 50) + "..."}"
                              </h4>
                              <p style={{ margin: 0, fontSize: 13, color: "var(--muted)", lineHeight: 1.45 }}>
                                {ad.copy}
                              </p>
                            </div>

                            {ad.score != null && (
                              <div style={{ textAlign: "right", flexShrink: 0 }}>
                                <div style={{ fontSize: 20, fontWeight: 700, color: "var(--accent)" }}>
                                  {ad.score}
                                  <span style={{ fontSize: 12, color: "var(--muted)" }}>/100</span>
                                </div>
                                <div style={{ fontSize: 11, color: "var(--muted)" }}>Creative score</div>
                              </div>
                            )}
                          </div>

                          {/* WHY THIS AD IS ATTRACTIVE - KEY REQUIREMENT HIGHLIGHT */}
                          <div
                            style={{
                              background: "var(--surface)",
                              border: "1px solid var(--line)",
                              borderLeft: "4px solid #0a7c6e",
                              borderRadius: 6,
                              padding: "14px 16px",
                              display: "flex",
                              flexDirection: "column",
                              gap: 6,
                            }}
                          >
                            <span style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#0a7c6e" }}>
                              Why this advertisement is attractive (Prospect psychology)
                            </span>
                            <p style={{ margin: 0, fontSize: 13, lineHeight: 1.55, color: "var(--ink)", fontWeight: 500 }}>
                              {ad.why || "The ad promises a concrete result in a fixed time, while offering a low-friction trial that removes hesitation."}
                            </p>
                          </div>

                          {/* Target Audience & Decoded Subtext */}
                          <div
                            style={{
                              background: "var(--canvas)",
                              border: "1px solid var(--line)",
                              borderRadius: 6,
                              padding: "12px 14px",
                              display: "grid",
                              gridTemplateColumns: "1fr 1fr",
                              gap: 12,
                              fontSize: 13,
                            }}
                          >
                            <div>
                              <strong style={{ display: "block", fontSize: 11, textTransform: "uppercase", color: "var(--muted)", marginBottom: 4 }}>
                                Target Audience
                              </strong>
                              <span style={{ color: "var(--ink)" }}>
                                {ad.audience || "Job seekers and recent graduates seeking verified career outcomes"}
                              </span>
                            </div>

                            <div>
                              <strong style={{ display: "block", fontSize: 11, textTransform: "uppercase", color: "var(--muted)", marginBottom: 4 }}>
                                Core Hook & Offer
                              </strong>
                              <span style={{ color: "var(--ink)" }}>
                                <strong>Hook:</strong> {ad.hook || "Outcome with timeline"} <br />
                                <strong>Offer:</strong> {ad.offer || "Demo class"}
                              </span>
                            </div>
                          </div>

                          {/* Tactics Chips */}
                          {ad.tactics && ad.tactics.length > 0 && (
                            <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                              <span style={{ fontSize: 11, fontWeight: 600, color: "var(--muted)" }}>Tactics used:</span>
                              {ad.tactics.map((t, idx) => (
                                <span key={idx} className="chip" style={{ background: "var(--canvas)", color: "var(--ink)" }}>
                                  {t}
                                </span>
                              ))}
                            </div>
                          )}

                          {/* Weakness & BrandMonk Opportunity */}
                          <div
                            style={{
                              background: "var(--warn-soft)",
                              border: "1px solid #f6d8a8",
                              borderRadius: 6,
                              padding: "10px 14px",
                              fontSize: 13,
                            }}
                          >
                            <strong style={{ color: "var(--warn)", display: "block", fontSize: 11, textTransform: "uppercase", marginBottom: 2 }}>
                              Vulnerability BrandMonk can exploit
                            </strong>
                            <span style={{ color: "#6b3b02" }}>
                              {ad.weak || "Competitor provides no verified salary data, instructor proof, or batch size transparency."}
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div
                  style={{
                    background: "var(--surface)",
                    border: "1px solid var(--line)",
                    borderRadius: 8,
                    padding: 40,
                    textAlign: "center",
                    color: "var(--muted)",
                  }}
                >
                  <p style={{ margin: 0, fontSize: 15, fontWeight: 500, color: "var(--ink)" }}>
                    No active ads found for {selectedCompany.name}
                  </p>
                  <p style={{ margin: "6px 0 0", fontSize: 13 }}>
                    Click "Refresh ads" to trigger a live crawl from Meta Ad Library, or choose another institution on the left.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: 60, color: "var(--muted)" }}>
              Select a competitor institution from the left panel to inspect their active ads and creative intelligence dossier.
            </div>
          )}
        </div>
      </div>

      {/* Creative Recommender Modal */}
      {recommenderAdId && (
        <CreativeRecommenderModal
          adId={recommenderAdId}
          isOpen={Boolean(recommenderAdId)}
          onClose={() => setRecommenderAdId(null)}
          competitorMediaUrl={recommenderMediaUrl}
        />
      )}
    </div>
  );
};
