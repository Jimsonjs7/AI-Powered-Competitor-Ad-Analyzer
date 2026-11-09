import React from "react";
import { Ad } from "../types";

interface AdPosterCardProps {
  ad: Ad;
  className?: string;
  sizeClass?: string;
}

export const AdPosterCard: React.FC<AdPosterCardProps> = ({ ad, className = "", sizeClass = "" }) => {
  // Palette styling based on course subject or id for consistent visual identity
  const palettes = [
    { bg: "#12324F", fg: "#FFFFFF", ac: "#F2B84B" },
    { bg: "#E3F3EC", fg: "#0E3B2E", ac: "#17795A" },
    { bg: "#2B1E5C", fg: "#FFFFFF", ac: "#FF8A5B" },
    { bg: "#FFD84D", fg: "#1A1A1A", ac: "#1A1A1A" },
    { bg: "#E9F0FF", fg: "#14284B", ac: "#3B5BDB" },
    { bg: "#FCE4E4", fg: "#5A1414", ac: "#D64545" },
  ];
  const p = palettes[ad.id % palettes.length];

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
