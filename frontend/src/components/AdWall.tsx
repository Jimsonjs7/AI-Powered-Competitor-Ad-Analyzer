import React from "react";
import { Ad } from "../types";
import { AdPosterCard } from "./AdPosterCard";

interface AdWallProps {
  ads: Ad[];
  selectedAdId: number | null;
  selectedCourse: string;
  sortBy: string;
  onSelectCourse: (course: string) => void;
  onSelectSort: (sort: string) => void;
  onSelectAd: (adId: number) => void;
}

export const AdWall: React.FC<AdWallProps> = ({
  ads,
  selectedAdId,
  selectedCourse,
  sortBy,
  onSelectCourse,
  onSelectSort,
  onSelectAd,
}) => {
  const competitorCount = new Set(ads.map((a) => a.competitor_name)).size;
  const courses = ["All", "AI", "Digital marketing", "UI/UX"];

  return (
    <main className="wall">
      <div className="read">
        <p>Most ads promise a result with a deadline.</p>
        <p>
          38% of active ads use it. UI/UX has the fewest ads in Coimbatore, which leaves room for BrandMonk.
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
        {ads.length > 0 ? (
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
