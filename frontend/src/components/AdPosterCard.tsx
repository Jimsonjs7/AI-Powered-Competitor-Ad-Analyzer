import React from "react";
import { Ad } from "../types";

interface AdPosterCardProps {
  ad: Ad;
  className?: string;
  sizeClass?: string;
}

export const AdPosterCard: React.FC<AdPosterCardProps> = ({ ad, className = "", sizeClass = "" }) => {
  const [imgError, setImgError] = React.useState(false);

  // Fallback color palette when no real image is available
  const palettes = [
    { bg: "#12324F", fg: "#FFFFFF", ac: "#F2B84B" },
    { bg: "#E3F3EC", fg: "#0E3B2E", ac: "#17795A" },
    { bg: "#2B1E5C", fg: "#FFFFFF", ac: "#FF8A5B" },
    { bg: "#FFD84D", fg: "#1A1A1A", ac: "#1A1A1A" },
    { bg: "#E9F0FF", fg: "#14284B", ac: "#3B5BDB" },
    { bg: "#FCE4E4", fg: "#5A1414", ac: "#D64545" },
  ];
  const p = palettes[ad.id % palettes.length];

  // Real image ad
  if (ad.media_url && ad.media_type !== "video" && !imgError) {
    return (
      <div
        className={`poster-img ${sizeClass} ${className}`.trim()}
        style={{ position: "relative", borderRadius: 6, overflow: "hidden", aspectRatio: "4/5", background: "#1B2421" }}
      >
        <img
          src={ad.media_url}
          alt={ad.headline || ad.course}
          style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
          loading="lazy"
          onError={() => setImgError(true)}
        />
        {/* Overlay chip + course label */}
        <div style={{ position: "absolute", top: 8, left: 8, display: "flex", gap: 4, flexWrap: "wrap" }}>
          <span style={{ background: "rgba(0,0,0,0.6)", color: "#fff", fontSize: 10, fontWeight: 700, padding: "2px 7px", borderRadius: 10, letterSpacing: "0.04em", textTransform: "uppercase" }}>
            {ad.course}
          </span>
          {ad.score != null && (
            <span style={{ background: "#0A7C6E", color: "#fff", fontSize: 10, fontWeight: 700, padding: "2px 7px", borderRadius: 10 }}>
              {ad.score}
            </span>
          )}
        </div>
      </div>
    );
  }

  // Video ad
  if (ad.media_url && ad.media_type === "video") {
    return (
      <a
        href={ad.media_url}
        target="_blank"
        rel="noreferrer"
        className={`poster-vid ${sizeClass} ${className}`.trim()}
        style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 8, background: "#1B2421", borderRadius: 6, aspectRatio: "4/5", textDecoration: "none", color: "#fff" }}
        aria-label={`Watch video ad by ${ad.competitor_name}`}
      >
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <polygon points="10 8 16 12 10 16 10 8" fill="#fff" stroke="none" />
        </svg>
        <span style={{ fontSize: 12, opacity: 0.75 }}>Watch video</span>
        <span style={{ background: "rgba(255,255,255,0.12)", color: "#fff", fontSize: 10, fontWeight: 700, padding: "2px 7px", borderRadius: 10, letterSpacing: "0.04em", textTransform: "uppercase" }}>
          {ad.course}
        </span>
      </a>
    );
  }

  // Fallback: color-block poster
  return (
    <div
      className={`poster ${sizeClass} ${className}`.trim()}
      style={
        {
          "--bg": p.bg,
          "--fg": p.fg,
          "--ac": p.ac,
        } as React.CSSProperties
      }
    >
      <span className="pt">{ad.tactics?.[0] || ad.course}</span>
      <h4>{ad.headline || ad.copy.slice(0, 40) + "..."}</h4>
      <p>{ad.copy.length > 70 ? ad.copy.slice(0, 68) + "..." : ad.copy}</p>
      <span className="pc">{ad.cta || "Enroll now"}</span>
    </div>
  );
};

