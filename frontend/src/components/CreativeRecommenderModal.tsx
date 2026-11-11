import React, { useEffect, useState } from "react";
import { fetchCreativeCounterRecommendations, renderPoster } from "../api/client";
import { CreativeCounterAdResponse } from "../types";

interface CreativeRecommenderModalProps {
  adId: number | null;
  isOpen: boolean;
  onClose: () => void;
  competitorMediaUrl?: string | null;
}

export const CreativeRecommenderModal: React.FC<CreativeRecommenderModalProps> = ({
  adId,
  isOpen,
  onClose,
  competitorMediaUrl,
}) => {
  const [data, setData] = useState<CreativeCounterAdResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [selectedAngleIndex, setSelectedAngleIndex] = useState(0);
  const [selectedRatio, setSelectedRatio] = useState<"1:1" | "4:5" | "9:16">("1:1");
  const [copyFeedback, setCopyFeedback] = useState("");

  // Poster render state
  const [isRenderingPoster, setIsRenderingPoster] = useState(false);
  const [renderedPosterUrl, setRenderedPosterUrl] = useState<string | null>(null);
  const [renderStatus, setRenderStatus] = useState("");

  useEffect(() => {
    if (isOpen && adId) {
      setIsLoading(true);
      setErrorMsg("");
      setData(null);
      setRenderedPosterUrl(null);
      setRenderStatus("");

      fetchCreativeCounterRecommendations(adId)
        .then((res) => {
          setData(res);
          setSelectedAngleIndex(0);
        })
        .catch((err) => {
          setErrorMsg(err.message || "Failed to generate creative recommendations");
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [isOpen, adId]);

  if (!isOpen || !adId) return null;

  const currentAngle = data ? data.angles[selectedAngleIndex] : null;

  const handleCopyText = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopyFeedback(`Copied ${label}.`);
      setTimeout(() => setCopyFeedback(""), 2500);
    } catch {
      setCopyFeedback("Copy failed.");
    }
  };

  const handleRenderPosterPreview = async () => {
    if (!currentAngle || !data) return;
    setIsRenderingPoster(true);
    setRenderStatus("Rendering background with BrandMonk layout...");
    try {
      const res = await renderPoster({
        ad_id: data.ad_id,
        course: data.course,
        angle_index: selectedAngleIndex,
        size_format: selectedRatio === "1:1" ? "square" : selectedRatio === "9:16" ? "story" : "feed",
        custom_headline: currentAngle.headline,
        custom_subline: currentAngle.subline,
        custom_cta: currentAngle.cta_text,
      });
      setRenderedPosterUrl(res.image_url);
      setRenderStatus("Branded poster rendered successfully.");
    } catch {
      setRenderStatus("Rendering failed. Verify image generation service.");
    } finally {
      setIsRenderingPoster(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
        zIndex: 120,
      }}
    >
      <div
        style={{
          background: "var(--surface)",
          borderRadius: 8,
          maxWidth: 1040,
          width: "100%",
          maxHeight: "92vh",
          display: "flex",
          flexDirection: "column",
          boxShadow: "0 14px 35px rgba(0,0,0,0.15)",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "16px 22px",
            borderBottom: "1px solid var(--line)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            background: "var(--surface)",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <h2 style={{ margin: 0, fontSize: 17 }}>Creative Counter-Ad Recommender</h2>
              <span className="chip" style={{ background: "var(--accent-soft)", color: "var(--accent)", fontSize: 11 }}>
                Strategic Inversion Engine
              </span>
            </div>
            <p style={{ margin: "2px 0 0", color: "var(--muted)", fontSize: 12 }}>
              Side-by-side tactical breakdown to out-position competitor ad spend with verified approved claims.
            </p>
          </div>
          <button className="btn" onClick={onClose} style={{ padding: "4px 10px" }}>
            Close
          </button>
        </div>

        {/* Content Body */}
        <div style={{ padding: 22, overflowY: "auto", flex: 1 }}>
          {isLoading ? (
            <div style={{ display: "grid", gridTemplateColumns: "360px 1fr", gap: 20 }}>
              <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, padding: 16, display: "flex", flexDirection: "column", gap: 14 }}>
                <div className="skeleton" style={{ width: 180, height: 20 }} />
                <div className="skeleton" style={{ width: "100%", height: 180, borderRadius: 6 }} />
                <div className="skeleton" style={{ width: 120, height: 16 }} />
                <div className="skeleton" style={{ width: "100%", height: 40 }} />
                <div className="skeleton" style={{ width: "100%", height: 60 }} />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                <div style={{ display: "flex", gap: 8 }}>
                  <div className="skeleton" style={{ flex: 1, height: 46, borderRadius: 6 }} />
                  <div className="skeleton" style={{ flex: 1, height: 46, borderRadius: 6 }} />
                  <div className="skeleton" style={{ flex: 1, height: 46, borderRadius: 6 }} />
                </div>
                <div className="skeleton" style={{ width: "100%", height: 90, borderRadius: 6 }} />
                <div className="skeleton" style={{ width: "100%", height: 220, borderRadius: 6 }} />
              </div>
            </div>
          ) : errorMsg ? (
            <div style={{ padding: 20, background: "var(--warn-soft)", color: "var(--warn)", borderRadius: 6 }}>
              {errorMsg}
            </div>
          ) : data && currentAngle ? (
            <div style={{ display: "grid", gridTemplateColumns: "360px 1fr", gap: 20 }}>
              {/* Left Column: Competitor Running Ad Audit */}
              <div
                style={{
                  background: "var(--canvas)",
                  border: "1px solid var(--line)",
                  borderRadius: 8,
                  padding: 16,
                  display: "flex",
                  flexDirection: "column",
                  gap: 14,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase" }}>
                    Competitor Ad Under Analysis
                  </span>
                  <span className="chip" style={{ fontSize: 11, background: "var(--warn-soft)", color: "var(--warn)" }}>
                    {data.competitor_audit.creative_fatigue_level}
                  </span>
                </div>

                {competitorMediaUrl && (
                  <img
                    src={competitorMediaUrl}
                    alt="Competitor Creative"
                    style={{ width: "100%", height: 160, objectFit: "cover", borderRadius: 6, border: "1px solid var(--line)" }}
                  />
                )}

                <div>
                  <h4 style={{ margin: "0 0 4px", fontSize: 14 }}>{data.competitor_audit.competitor_name}</h4>
                  {data.competitor_audit.headline && (
                    <div style={{ fontSize: 13, fontWeight: 600, color: "var(--ink)", marginBottom: 4 }}>
                      "{data.competitor_audit.headline}"
                    </div>
                  )}
                  <p style={{ margin: 0, fontSize: 12, color: "var(--muted)", lineHeight: 1.4, maxHeight: 75, overflow: "hidden" }}>
                    {data.competitor_audit.copy_snippet}
                  </p>
                </div>

                {/* Detected Vulnerabilities */}
                <div style={{ borderTop: "1px solid var(--line)", paddingTop: 10 }}>
                  <span style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--danger)", marginBottom: 6 }}>
                    Identified Flaws & Vulnerabilities:
                  </span>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {data.competitor_audit.vulnerabilities.map((v, i) => (
                      <div
                        key={i}
                        style={{
                          fontSize: 12,
                          background: "var(--surface)",
                          padding: "6px 8px",
                          borderRadius: 4,
                          borderLeft: "3px solid var(--danger)",
                        }}
                      >
                        {v}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Unaddressed Prospect Doubts */}
                <div style={{ borderTop: "1px solid var(--line)", paddingTop: 10 }}>
                  <span style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--muted)", marginBottom: 6 }}>
                    Doubts Left in Prospect Minds:
                  </span>
                  <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: "var(--muted)", lineHeight: 1.4 }}>
                    {data.competitor_audit.unaddressed_prospect_doubts.map((d, i) => (
                      <li key={i} style={{ marginBottom: 4 }}>{d}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Right Column: Creative Recommender Hub */}
              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                {/* Angle Selector */}
                <div style={{ display: "flex", gap: 8 }}>
                  {data.angles.map((angle, idx) => (
                    <button
                      key={angle.angle_type}
                      className="fl"
                      aria-pressed={selectedAngleIndex === idx}
                      onClick={() => {
                        setSelectedAngleIndex(idx);
                        setRenderedPosterUrl(null);
                      }}
                      style={{
                        fontSize: 12,
                        minHeight: 46,
                        height: "auto",
                        padding: "8px 12px",
                        lineHeight: 1.35,
                        flex: 1,
                        textAlign: "center",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        whiteSpace: "normal",
                      }}
                    >
                      {angle.angle_name}
                    </button>
                  ))}
                </div>

                {/* Strategic Rationale Banner */}
                <div
                  style={{
                    padding: "14px 16px",
                    background: "var(--surface)",
                    borderRadius: 6,
                    border: "1px solid var(--line)",
                    borderLeft: "4px solid #0a7c6e",
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <span
                      style={{
                        fontSize: 11,
                        fontWeight: 700,
                        textTransform: "uppercase",
                        letterSpacing: "0.06em",
                        color: "var(--muted)",
                      }}
                    >
                      Strategic positioning advantage
                    </span>
                    <span
                      className="chip"
                      style={{
                        fontSize: 11,
                        background: "var(--canvas)",
                        color: "var(--ink)",
                        fontWeight: 600,
                        border: "1px solid var(--line)",
                      }}
                    >
                      Counter-angle
                    </span>
                  </div>
                  <div style={{ fontSize: 13, color: "var(--ink)", lineHeight: 1.5, fontWeight: 500 }}>
                    {currentAngle.strategic_rationale}
                  </div>
                  <div
                    style={{
                      fontSize: 12,
                      background: "var(--canvas)",
                      border: "1px solid var(--line)",
                      borderRadius: 4,
                      padding: "8px 12px",
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                    }}
                  >
                    <span style={{ color: "#0a7c6e", fontWeight: 700, fontSize: 13 }}>✓</span>
                    <span style={{ color: "var(--ink)" }}>
                      <strong style={{ color: "var(--muted)" }}>Backed by approved claim:</strong> "{currentAngle.matching_approved_claim}"
                    </span>
                  </div>
                </div>

                {/* Copy Deck Card */}
                <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 6, padding: 14 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)" }}>
                      Ad Copy Deck
                    </span>
                    {copyFeedback && (
                      <span style={{ fontSize: 12, color: "var(--accent)", fontWeight: 500 }}>
                        {copyFeedback}
                      </span>
                    )}
                  </div>

                  {/* Headline */}
                  <div style={{ marginBottom: 10 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 2 }}>
                      <span style={{ fontSize: 11, color: "var(--muted)", fontWeight: 600 }}>PUNCHY HEADLINE (&lt;8 words)</span>
                      <button
                        className="btn"
                        onClick={() => handleCopyText(currentAngle.headline, "headline")}
                        style={{ fontSize: 11, padding: "2px 6px" }}
                      >
                        Copy
                      </button>
                    </div>
                    <div style={{ fontSize: 15, fontWeight: 700, color: "var(--ink)" }}>
                      {currentAngle.headline}
                    </div>
                  </div>

                  {/* Subline */}
                  <div style={{ marginBottom: 10 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 2 }}>
                      <span style={{ fontSize: 11, color: "var(--muted)", fontWeight: 600 }}>SUPPORTING SUBLINE</span>
                      <button
                        className="btn"
                        onClick={() => handleCopyText(currentAngle.subline, "subline")}
                        style={{ fontSize: 11, padding: "2px 6px" }}
                      >
                        Copy
                      </button>
                    </div>
                    <div style={{ fontSize: 13, color: "var(--muted)" }}>
                      {currentAngle.subline}
                    </div>
                  </div>

                  {/* Primary Ad Copy */}
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 2 }}>
                      <span style={{ fontSize: 11, color: "var(--muted)", fontWeight: 600 }}>PRIMARY AD TEXT (BODY)</span>
                      <button
                        className="btn"
                        onClick={() => handleCopyText(currentAngle.primary_text, "primary copy")}
                        style={{ fontSize: 11, padding: "2px 6px" }}
                      >
                        Copy Full Copy
                      </button>
                    </div>
                    <div
                      style={{
                        fontSize: 12,
                        background: "var(--canvas)",
                        padding: "8px 10px",
                        borderRadius: 4,
                        whiteSpace: "pre-wrap",
                        lineHeight: 1.45,
                        fontFamily: "inherit",
                      }}
                    >
                      {currentAngle.primary_text}
                    </div>
                  </div>
                </div>

                {/* AI Visual Generator & Art Direction */}
                <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 6, padding: 14 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", color: "var(--muted)" }}>
                      AI Image Generation Brief & Prompt
                    </span>
                    <div style={{ display: "flex", gap: 4 }}>
                      {(["1:1", "4:5", "9:16"] as const).map((r) => (
                        <button
                          key={r}
                          className="fl"
                          aria-pressed={selectedRatio === r}
                          onClick={() => setSelectedRatio(r)}
                          style={{ fontSize: 11, padding: "2px 8px" }}
                        >
                          {r}
                        </button>
                      ))}
                    </div>
                  </div>

                  <p style={{ margin: "0 0 8px", fontSize: 12, color: "var(--muted)" }}>
                    <strong>Art Direction:</strong> {currentAngle.visual_concept}
                  </p>

                  <div
                    style={{
                      background: "var(--canvas)",
                      padding: 10,
                      borderRadius: 4,
                      fontSize: 12,
                      fontFamily: "monospace",
                      lineHeight: 1.4,
                      marginBottom: 10,
                      border: "1px solid var(--line)",
                    }}
                  >
                    {currentAngle.aspect_ratios[selectedRatio] || currentAngle.image_prompt}
                  </div>

                  <div style={{ display: "flex", gap: 8, justifyContent: "space-between", alignItems: "center" }}>
                    <button
                      className="btn"
                      onClick={() =>
                        handleCopyText(
                          currentAngle.aspect_ratios[selectedRatio] || currentAngle.image_prompt,
                          "AI image prompt"
                        )
                      }
                      style={{ fontSize: 12 }}
                    >
                      Copy Midjourney / Flux Prompt
                    </button>

                    <button
                      className="btn pri"
                      disabled={isRenderingPoster}
                      onClick={handleRenderPosterPreview}
                      style={{ fontSize: 12 }}
                    >
                      {isRenderingPoster ? "Rendering..." : "Render Poster Preview"}
                    </button>
                  </div>

                  {renderStatus && (
                    <div style={{ marginTop: 8, fontSize: 12, color: "var(--accent)" }}>
                      {renderStatus}
                    </div>
                  )}

                  {renderedPosterUrl && (
                    <div style={{ marginTop: 12, borderTop: "1px solid var(--line)", paddingTop: 10 }}>
                      <span style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 6 }}>
                        Live Rendered Branded Poster:
                      </span>
                      <img
                        src={renderedPosterUrl}
                        alt="Rendered Poster"
                        style={{ maxWidth: "100%", maxHeight: 260, objectFit: "contain", borderRadius: 4, border: "1px solid var(--line)" }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

