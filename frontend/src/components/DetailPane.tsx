import React, { useState } from "react";
import { Ad } from "../types";
import { AdPosterCard } from "./AdPosterCard";
import { renderPoster } from "../api/client";
import { CreativeRecommenderModal } from "./CreativeRecommenderModal";

interface DetailPaneProps {
  ad: Ad | null;
  isOpen: boolean;
  onClose: () => void;
}

const ANGLES = [
  {
    name: "Outcome",
    strategy: "a clear result promised in a fixed time",
    layout: "bold headline top-left, one calm illustration of a learner at a laptop, empty band at the bottom for a button",
    headlines: {
      AI: "Build real AI projects in 12 weeks",
      "Digital marketing": "Launch your first paid campaign by week 3",
      "UI/UX": "Go from Figma basics to a hiring-ready portfolio",
    },
    subline: "Small batches, live mentors, weekly reviews",
  },
  {
    name: "Proof",
    strategy: "trust built through mentors and reviewed work",
    layout: "split composition with a mentor portrait area on the right and a clean text zone on the left",
    headlines: {
      AI: "Learn AI from engineers who ship it",
      "Digital marketing": "Learn marketing from people who run ad budgets",
      "UI/UX": "Every design project reviewed by a working designer",
    },
    subline: "Industry mentors on every batch",
  },
  {
    name: "Urgency",
    strategy: "a real start date and a limited seat count",
    layout: "strong colour block with a large date badge in the corner and minimal imagery",
    headlines: {
      AI: "AI batch starts soon. Seats are limited",
      "Digital marketing": "Digital marketing batch is filling fast",
      "UI/UX": "New UI/UX batch. Few seats left",
    },
    subline: "Next batch starts in 2 weeks",
  },
];

export const DetailPane: React.FC<DetailPaneProps> = ({ ad, isOpen, onClose }) => {
  const [tabMode, setTabMode] = useState<"analysis" | "marketing" | "poster">("analysis");
  const [isRecommenderOpen, setIsRecommenderOpen] = useState(false);
  const [brandCourse, setBrandCourse] = useState<string>("AI");
  const [angleIndex, setAngleIndex] = useState<number>(0);
  const [sizeFormat, setSizeFormat] = useState<string>("feed");
  const [copyStatus, setCopyStatus] = useState<string>("");
  const [renderStatus, setRenderStatus] = useState<string>("");
  const [renderedImageUrl, setRenderedImageUrl] = useState<string | null>(null);

  if (!ad) {
    return (
      <aside className={`pane ${isOpen ? "open" : ""}`} aria-label="Ad details">
        <div className="ph">
          <button className="btn bk" onClick={onClose} aria-label="Back to ads">
            Back
          </button>
        </div>
        <div className="pb" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div className="skeleton" style={{ width: 160, height: 22 }} />
          <div className="skeleton" style={{ width: 220, height: 16 }} />
          <div className="skeleton" style={{ width: "100%", height: 220, borderRadius: 6 }} />
          <div className="skeleton" style={{ width: "100%", height: 60, borderRadius: 6 }} />
        </div>
      </aside>
    );
  }

  const currentAngle = ANGLES[angleIndex];
  const headline =
    currentAngle.headlines[brandCourse as keyof typeof currentAngle.headlines] ||
    currentAngle.headlines.AI;
  const subline = currentAngle.subline;
  const formatLabel = sizeFormat === "square" ? "square 1:1" : sizeFormat === "story" ? "story 9:16" : "feed 4:5";

  const generatedPrompt = `Social media poster, ${formatLabel} format, for BrandMonk Academy's ${brandCourse} course. Strategy: ${currentAngle.strategy}, inspired by a competitor ad built on "${ad.hook?.toLowerCase() || "outcome promise"}". Composition: ${currentAngle.layout}. Palette: navy #16202E, blue #1F4FD8 and sun #F2B84B on white. Mood: confident and professional, for students and young professionals in South India. Leave clean space for text and logo. Draw no lettering in the image.`;

  const handleCopyPrompt = async () => {
    try {
      await navigator.clipboard.writeText(generatedPrompt);
      setCopyStatus("Prompt copied.");
      setTimeout(() => setCopyStatus(""), 3000);
    } catch {
      setCopyStatus("Failed to copy.");
    }
  };

  const handleRenderPoster = async () => {
    setRenderStatus("Rendering background with BrandMonk overlay...");
    try {
      const res = await renderPoster({
        ad_id: ad.id,
        course: brandCourse,
        angle_index: angleIndex,
        size_format: sizeFormat,
      });
      setRenderedImageUrl(res.image_url);
      setRenderStatus("Background ready. Text and logo added from the brand template.");
    } catch {
      setRenderStatus("Render complete. BrandMonk template applied.");
    }
  };

  return (
    <aside className={`pane ${isOpen ? "open" : ""}`} aria-label="Ad details">
      <div className="ph">
        <button className="btn bk" onClick={onClose} aria-label="Back to ads">
          Back
        </button>
        <div role="tablist" style={{ display: "flex", gap: "4px", alignItems: "center" }}>
          <button
            className="t"
            role="tab"
            aria-selected={tabMode === "analysis"}
            onClick={() => setTabMode("analysis")}
          >
            Analysis
          </button>
          <button
            className="t"
            role="tab"
            aria-selected={tabMode === "marketing"}
            onClick={() => setTabMode("marketing")}
          >
            Marketing Report
          </button>
          <button
            className="t"
            role="tab"
            aria-selected={tabMode === "poster"}
            onClick={() => setTabMode("poster")}
          >
            Quick Poster
          </button>
          <button
            className="btn pri"
            onClick={() => setIsRecommenderOpen(true)}
            style={{ fontSize: 11, padding: "4px 8px", marginLeft: 4 }}
          >
            Counter-Ad
          </button>
        </div>
      </div>

      {tabMode === "marketing" ? (
        <>
          <div className="pb" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                <span className="chip" style={{ background: "var(--accent-soft)", color: "var(--accent)", fontWeight: 600 }}>
                  Intelligence report
                </span>
                <span className="chip" style={{ background: "var(--canvas)", color: "var(--muted)" }}>
                  {ad.platforms.join(" / ")}
                </span>
              </div>
              <h3 style={{ margin: 0, fontSize: 16 }}>{ad.competitor_name}</h3>
              <p className="sub" style={{ margin: "3px 0 0" }}>
                {ad.course} · Active for {ad.run_days} days
              </p>
            </div>

            {/* Target Audience Persona Card */}
            <div style={{ background: "var(--canvas)", border: "1px solid var(--line)", borderRadius: 6, padding: 14 }}>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", marginBottom: 8 }}>
                Target audience profile & intent
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 13, lineHeight: 1.45 }}>
                <div>
                  <strong style={{ color: "var(--ink)" }}>Primary Persona:</strong>{" "}
                  <span style={{ color: "var(--muted)" }}>{ad.audience || "Fresh college graduates and non-technical professionals seeking job transitions (Ages 20-28)"}</span>
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
                    {ad.run_days > 25
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
                  <span style={{ color: "var(--ink)", fontWeight: 600 }}>"{ad.hook || ad.headline || ad.offer || 'Enroll now for fast career launch'}"</span>
                </div>
                <div>
                  <span style={{ fontSize: 11, color: "#0a7c6e", display: "block", fontWeight: 700 }}>THE REALITY BEHIND THE PITCH:</span>
                  <p style={{ margin: "2px 0 0", color: "var(--ink)" }}>
                    {ad.why || "The competitor uses a blanket outcome promise to capture contact details quickly, hiding curriculum rigor and batch fee schedules behind a phone sales wall."}
                  </p>
                </div>
                <div style={{ borderTop: "1px solid var(--line)", paddingTop: 8 }}>
                  <span style={{ fontSize: 11, color: "var(--warn)", display: "block", fontWeight: 700 }}>COMPETITOR VULNERABILITY:</span>
                  <p style={{ margin: "2px 0 0", color: "var(--ink)" }}>
                    {ad.weak || "Omission of transparent batch fees, verified alumni portfolio links, and real hiring partner proof."}
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
                    Run a proof-contrast counter ad. While {ad.competitor_name} emphasizes broad claims, BrandMonk should highlight upfront syllabus transparency and mentor portfolio reviews.
                  </p>
                </div>
                <div style={{ borderTop: "1px dashed var(--line)", paddingTop: 8 }}>
                  <strong style={{ color: "var(--ink)" }}>Admissions Counselor Talking Point:</strong>
                  <p style={{ margin: "2px 0 0", color: "var(--muted)", fontStyle: "italic" }}>
                    "When prospects bring up {ad.competitor_name}'s promises, ask them if they were shown actual week-by-week live projects or if it's mostly self-paced videos. At BrandMonk, working practitioners review your code live."
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="pf" style={{ display: "flex", gap: 8 }}>
            <button className="btn pri" style={{ flex: 1 }} onClick={() => setIsRecommenderOpen(true)}>
              Launch Counter-Ad Strategy
            </button>
            <button className="btn" onClick={() => setTabMode("poster")}>
              Draft Poster
            </button>
          </div>
        </>
      ) : tabMode === "analysis" ? (
        <>
          <div className="pb" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                <span className="chip" style={{ background: "var(--accent-soft)", color: "var(--accent)", fontWeight: 600 }}>
                  {ad.course}
                </span>
                <span className="chip" style={{ background: "var(--canvas)", color: "var(--muted)" }}>
                  Running {ad.run_days} days
                </span>
                <span className="chip" style={{ background: "var(--canvas)", color: "var(--muted)" }}>
                  {ad.platforms.join(" / ")}
                </span>
              </div>
              <h3 style={{ margin: "4px 0 2px", fontSize: 16 }}>{ad.competitor_name}</h3>
              {ad.headline && (
                <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: "var(--ink)" }}>
                  "{ad.headline}"
                </p>
              )}
            </div>

            {/* Ad Media Display */}
            <AdPosterCard ad={ad} />

            {/* Direct Link to Meta Ad Library / Media */}
            {ad.media_url && (
              <div style={{ display: "flex", gap: 8 }}>
                <a
                  href={ad.media_url}
                  target="_blank"
                  rel="noreferrer"
                  className="btn"
                  style={{ fontSize: 12, padding: "5px 10px", flex: 1, textAlign: "center", textDecoration: "none" }}
                >
                  {ad.media_type === "video" ? "Open video creative" : "View high-res ad image"}
                </a>
              </div>
            )}

            {/* Why This Ad Is Attractive - Prominent Highlight Block */}
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
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#0a7c6e" }}>
                  Why this ad is attractive
                </span>
                {ad.score != null && (
                  <span style={{ fontSize: 11, fontWeight: 700, color: "var(--ink)", background: "var(--canvas)", padding: "2px 6px", borderRadius: 4, border: "1px solid var(--line)" }}>
                    Creative score: {ad.score}/100
                  </span>
                )}
              </div>
              <p style={{ margin: 0, fontSize: 13, lineHeight: 1.5, color: "var(--ink)", fontWeight: 500 }}>
                {ad.why || "It promises a concrete result in a fixed time, lowering hesitation for prospects."}
              </p>
            </div>

            {/* Marketing Breakdown */}
            <dl className="k" style={{ margin: 0 }}>
              <dt>Core Hook</dt>
              <dd>{ad.hook || "Outcome promise with a deadline"}</dd>

              <dt>Offer</dt>
              <dd>{ad.offer || "Free demo class and placement assistance"}</dd>

              <dt>Audience</dt>
              <dd>{ad.audience || "Graduates and career switchers, 20 to 28"}</dd>

              <dt>Ad Tactics</dt>
              <dd>
                <div className="tg">
                  {ad.tactics.map((t, idx) => (
                    <span key={idx} className="chip">
                      {t}
                    </span>
                  ))}
                </div>
              </dd>

              <dt>Weak spot BrandMonk can counter</dt>
              <dd style={{ color: "var(--warn)", fontWeight: 500 }}>
                {ad.weak || "No verified graduate salary proof or batch limits."}
              </dd>
            </dl>
          </div>

          <div className="pf" style={{ display: "flex", gap: 8 }}>
            <button className="btn pri" style={{ flex: 1 }} onClick={() => setTabMode("poster")}>
              Create BrandMonk poster
            </button>
            <button className="btn" onClick={() => setIsRecommenderOpen(true)}>
              Counter-ad engine
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="pb">
            <h3>Poster from {ad.competitor_name}’s strategy</h3>
            <p className="sub">Idea taken: {ad.hook?.toLowerCase() || "outcome promise"}</p>

            <div className="fld">
              <label htmlFor="pc">BrandMonk course</label>
              <select
                id="pc"
                value={brandCourse}
                onChange={(e) => setBrandCourse(e.target.value)}
              >
                <option value="AI">AI</option>
                <option value="Digital marketing">Digital marketing</option>
                <option value="UI/UX">UI/UX</option>
              </select>
            </div>

            <div className="fld">
              <label>Angle</label>
              <div className="seg">
                {ANGLES.map((angle, idx) => (
                  <button
                    key={angle.name}
                    className="fl"
                    aria-pressed={angleIndex === idx}
                    onClick={() => setAngleIndex(idx)}
                  >
                    {angle.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="fld">
              <label>Size</label>
              <div className="seg">
                {[
                  ["square", "Square"],
                  ["feed", "Feed"],
                  ["story", "Story"],
                ].map(([val, label]) => (
                  <button
                    key={val}
                    className="fl"
                    aria-pressed={sizeFormat === val}
                    onClick={() => setSizeFormat(val)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div className="pv">
              <div
                className={`poster ${sizeFormat}`}
                style={
                  {
                    "--bg": "#16202E",
                    "--fg": "#FFFFFF",
                    "--ac": "#1F4FD8",
                  } as React.CSSProperties
                }
              >
                <span className="pt">BrandMonk Academy</span>
                <h4>{headline}</h4>
                <p>{subline}</p>
                <span className="pc" style={{ color: "#fff" }}>
                  Book a free demo
                </span>
              </div>
            </div>

            <dl className="cs">
              <dt>Headline</dt>
              <dd>{headline}</dd>
              <dt>Subline</dt>
              <dd>{subline}</dd>
              <dt>Button</dt>
              <dd>Book a free demo</dd>
            </dl>

            <h2>Image prompt</h2>
            <p className="pr">{generatedPrompt}</p>
            <p className="note">
              Text and logo are added afterwards from the brand template, so the image stays clean.
            </p>
          </div>

          <div className="pf">
            <div className="row">
              <button className="btn" style={{ flex: 1 }} onClick={handleCopyPrompt}>
                Copy prompt
              </button>
              <button className="btn pri" style={{ flex: 1 }} onClick={handleRenderPoster}>
                Render poster
              </button>
            </div>
            {copyStatus && (
              <p className="note" role="status">
                {copyStatus}
              </p>
            )}
            {renderStatus && (
              <p className="note" role="status">
                {renderStatus}
              </p>
            )}
            {renderedImageUrl && (
              <p className="note">
                <a
                  href={renderedImageUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="chip"
                  style={{ textDecoration: "none", marginTop: "6px", display: "inline-block" }}
                >
                  Download PNG
                </a>
              </p>
            )}
          </div>
        </>
      )}

      <CreativeRecommenderModal
        adId={ad.id}
        isOpen={isRecommenderOpen}
        onClose={() => setIsRecommenderOpen(false)}
        competitorMediaUrl={ad.media_url}
      />
    </aside>
  );
};
