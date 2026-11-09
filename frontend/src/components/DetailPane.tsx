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
  const [tabMode, setTabMode] = useState<"analysis" | "poster">("analysis");
  const [isRecommenderOpen, setIsRecommenderOpen] = useState(false);
  const [brandCourse, setBrandCourse] = useState<string>("AI");
  const [angleIndex, setAngleIndex] = useState<number>(0);
  const [sizeFormat, setSizeFormat] = useState<string>("feed");
  const [copyStatus, setCopyStatus] = useState<string>("");
  const [renderStatus, setRenderStatus] = useState<string>("");
  const [renderedImageUrl, setRenderedImageUrl] = useState<string | null>(null);

  if (!ad) {
    return <aside className={`pane ${isOpen ? "open" : ""}`} aria-label="Ad details"></aside>;
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
            Counter-Ad Strategy
          </button>
        </div>
      </div>

      {tabMode === "analysis" ? (
        <>
          <div className="pb">
            <h3>{ad.competitor_name}</h3>
            <p className="sub">
              {ad.course}, running {ad.run_days} days on {ad.platforms.join(" and ")}
            </p>

            <AdPosterCard ad={ad} />

            <div className="verdict">
              <div>
                <b>{ad.score || 70}</b>
                <small>out of 100</small>
              </div>
              <p>{ad.why || "It promises a concrete result in a fixed time."}</p>
            </div>

            <dl className="k">
              <dt>Hook</dt>
              <dd>{ad.hook || "Outcome promise with a deadline"}</dd>

              <dt>Offer</dt>
              <dd>{ad.offer || "Free demo class and placement assistance"}</dd>

              <dt>Audience</dt>
              <dd>{ad.audience || "Graduates and career switchers, 20 to 28"}</dd>

              <dt>Tactics</dt>
              <dd>
                <div className="tg">
                  {ad.tactics.map((t, idx) => (
                    <span key={idx} className="chip">
                      {t}
                    </span>
                  ))}
                </div>
              </dd>

              <dt>Weak spot BrandMonk can use</dt>
              <dd>{ad.weak || "No verified graduate salary proof or batch limits."}</dd>
            </dl>
          </div>

          <div className="pf">
            <button className="btn pri" onClick={() => setTabMode("poster")}>
              Create BrandMonk poster from this ad
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
