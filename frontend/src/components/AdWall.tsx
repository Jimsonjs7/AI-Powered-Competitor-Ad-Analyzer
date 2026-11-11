import React from "react";
import { Ad, MarketInsight } from "../types";
import { AdPosterCard } from "./AdPosterCard";

interface AdWallProps {
  ads: Ad[];
  marketInsight: MarketInsight | null;
  selectedAdId: number | null;
  selectedCourse: string;
  sortBy: string;
  isLoading?: boolean;
  onSelectCourse: (course: string) => void;
  onSelectSort: (sort: string) => void;
  onSelectAd: (adId: number) => void;
}

export const AdWall: React.FC<AdWallProps> = ({
  ads,
  marketInsight,
  selectedAdId,
  selectedCourse,
  sortBy,
  isLoading = false,
  onSelectCourse,
  onSelectSort,
  onSelectAd,
}) => {
  const competitorCount = new Set(ads.map((a) => a.competitor_name)).size;
  const courses = ["All", "AI", "Digital marketing", "UI/UX"];

  return (
    <main className="wall">
      <div className="read">
        <p>{marketInsight?.headline || "Tracking competitor creatives."}</p>
        <p>
          {marketInsight?.subline || "Add competitors or click Refresh ads to fetch live Meta creatives."}
        </p>
      </div>

      <div className="bar">
        {courses.map((c) => (
          <button
            key={c}
            className="fl"
            aria-pressed={selectedCourse === c}
            onClick={() => onSelectCourse(c)}
          >
            {c === "All" ? "All courses" : c}
          </button>
        ))}

        <div className="sp">
          <label htmlFor="so">Sort by</label>
          <select
            id="so"
            value={sortBy}
            onChange={(e) => onSelectSort(e.target.value)}
          >
            <option value="days">Longest running</option>
            <option value="score">Highest score</option>
            <option value="new">Newest</option>
          </select>
        </div>

        <p className="cnt" role="status">
          {ads.length} ads from {competitorCount} competitors
        </p>
      </div>

      <div className="gal">
        {isLoading ? (
          [1, 2, 3, 4, 5, 6].map((idx) => (
            <div
              key={idx}
              className="tile"
              style={{
                background: "var(--surface)",
                cursor: "default",
                padding: 10,
                display: "flex",
                flexDirection: "column",
                gap: 8,
              }}
            >
              <div
                className="skeleton"
                style={{
                  width: "100%",
                  aspectRatio: "4 / 5",
                  borderRadius: 6,
                }}
              />
              <div className="skeleton" style={{ width: "70%", height: 16 }} />
              <div className="skeleton" style={{ width: "40%", height: 12 }} />
            </div>
          ))
        ) : ads.length > 0 ? (
          ads.map((ad) => {
            const isSelected = ad.id === selectedAdId;
            const progressPct = Math.min(100, (ad.run_days / 90) * 100);

            return (
              <button
                key={ad.id}
                className="tile"
                data-id={ad.id}
                aria-pressed={isSelected}
                onClick={() => onSelectAd(ad.id)}
              >
                <AdPosterCard ad={ad} />
                <b>{ad.competitor_name}</b>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", margin: "2px 0 3px", fontSize: 11 }}>
                  <span style={{ color: "var(--accent)", fontWeight: 600 }}>{ad.course}</span>
                  <span style={{ color: "var(--muted)" }}>{ad.platforms.join("/")}</span>
                </div>
                <div className="rl">
                  <i style={{ width: `${progressPct}%` }}></i>
                </div>
                <span>Running {ad.run_days} days</span>
              </button>
            );
          })
        ) : (
          <p className="empty">
            No ads match these filters. Select more competitors or choose All courses.
          </p>
        )}
      </div>
    </main>
  );
};
