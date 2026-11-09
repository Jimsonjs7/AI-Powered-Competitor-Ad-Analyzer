import React, { useState } from "react";
import { Competitor } from "../types";

interface CompetitorRailProps {
  competitors: Competitor[];
  selectedNames: Set<string>;
  onToggleCompetitor: (name: string, checked: boolean) => void;
  onAddCompetitor: (nameOrUrl: string) => void;
}

export const CompetitorRail: React.FC<CompetitorRailProps> = ({
  competitors,
  selectedNames,
  onToggleCompetitor,
  onAddCompetitor,
}) => {
  const [inputVal, setInputVal] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputVal.trim()) {
      onAddCompetitor(inputVal.trim());
      setInputVal("");
    }
  };

  return (
    <aside className="rail" aria-label="Competitors">
      <h2>Competitors to watch</h2>
      <div style={{ display: "contents" }}>
        {competitors.map((comp) => {
          const isChecked = selectedNames.has(comp.name);
          const needsReview = comp.confidence === "needs_review" || comp.confidence === "low";

          return (
            <label key={comp.id} className="co">
              <input
                type="checkbox"
                checked={isChecked}
                onChange={(e) => onToggleCompetitor(comp.name, e.target.checked)}
              />
              <div>
                <b>{comp.name}</b>
                <span>
                  {comp.course}, {comp.active_ads_count} active ads
                </span>
                {needsReview && <span className="chip w">Needs review</span>}
              </div>
            </label>
          );
        })}
      </div>
      <form className="add" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Institute or Page link"
          aria-label="Add a competitor"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
        />
        <button type="submit" className="btn">
          Add
        </button>
      </form>
    </aside>
  );
};

