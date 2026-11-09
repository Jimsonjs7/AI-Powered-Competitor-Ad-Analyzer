import React, { useState } from "react";
import { startDiscovery } from "../api/client";

interface TopBarProps {
  currentView: "wall" | "competitors" | "opportunities" | "profile" | "notes";
  onSelectView: (view: "wall" | "competitors" | "opportunities" | "profile" | "notes") => void;
  statusText: string;
  selectedCity: string;
  onCityChange: (city: string) => void;
  onRefreshAds: () => void;
  isRefreshing: boolean;
  completenessScore?: number;
}

export const TopBar: React.FC<TopBarProps> = ({
  currentView,
  onSelectView,
  statusText,
  selectedCity,
  onCityChange,
  onRefreshAds,
  isRefreshing,
  completenessScore,
}) => {
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [discoveryMsg, setDiscoveryMsg] = useState("");

  const handleStartDiscovery = async () => {
    setIsDiscovering(true);
    setDiscoveryMsg("Starting discovery agent...");
    try {
      const res = await startDiscovery(15.0);
      setDiscoveryMsg(`Agent started (Run #${res.run_id})`);
      setTimeout(() => setDiscoveryMsg(""), 4000);
    } catch (err) {
      setDiscoveryMsg("Discovery failed to start.");
      setTimeout(() => setDiscoveryMsg(""), 3000);
    } finally {
      setIsDiscovering(false);
    }
  };

  return (
    <header className="top" style={{ display: "flex", alignItems: "center", gap: 12, padding: "0 18px", borderBottom: "1px solid var(--line)", background: "var(--surface)" }}>
      <div className="brand" style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }} onClick={() => onSelectView("wall")}>
        <span className="mark">B</span>
        <span>Ad Desk <span style={{ fontSize: 11, background: "var(--accent-soft)", color: "var(--accent)", padding: "1px 6px", borderRadius: 4 }}>v2</span></span>
      </div>

      {/* Primary Navigation Tabs */}
      <nav style={{ display: "flex", gap: 6 }}>
        <button
          className="fl"
          aria-pressed={currentView === "wall"}
          onClick={() => onSelectView("wall")}
          style={{ fontSize: 13, padding: "5px 10px" }}
        >
          Ad Wall
        </button>
        <button
          className="fl"
          aria-pressed={currentView === "competitors"}
          onClick={() => onSelectView("competitors")}
          style={{ fontSize: 13, padding: "5px 10px" }}
        >
          Competitors
        </button>
        <button
          className="fl"
          aria-pressed={currentView === "opportunities"}
          onClick={() => onSelectView("opportunities")}
          style={{ fontSize: 13, padding: "5px 10px" }}
        >
          Opportunities
        </button>
        <button
          className="fl"
          aria-pressed={currentView === "profile"}
          onClick={() => onSelectView("profile")}
          style={{ fontSize: 13, padding: "5px 10px" }}
        >
          Profile
          {completenessScore !== undefined && (
            <span style={{ marginLeft: 6, fontSize: 10, background: completenessScore >= 70 ? "var(--accent-soft)" : "var(--warn-soft)", color: completenessScore >= 70 ? "var(--accent)" : "var(--warn)", padding: "1px 5px", borderRadius: 10 }}>
              {completenessScore}%
            </span>
          )}
        </button>
      </nav>

      {/* Discovery Status / Feedback */}
      {discoveryMsg && (
        <span style={{ fontSize: 12, color: "var(--accent)", fontWeight: 500 }} role="status">
          {discoveryMsg}
        </span>
      )}

      {/* Actions on the right */}
      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 10 }}>
        <span className="src" role="status" style={{ fontSize: 12 }}>
          <i></i>
          {statusText}
        </span>

        <select
          aria-label="City"
          value={selectedCity}
          onChange={(e) => onCityChange(e.target.value)}
          style={{ fontSize: 13, padding: "4px 8px" }}
        >
          <option value="Coimbatore">Coimbatore</option>
          <option value="Kochi">Kochi</option>
          <option value="Bengaluru">Bengaluru</option>
        </select>

        <button
          className="btn"
          disabled={isDiscovering}
          onClick={handleStartDiscovery}
          style={{ fontSize: 13 }}
        >
          {isDiscovering ? "Discovering..." : "Find competitors"}
        </button>

        <button
          className="btn pri"
          onClick={onRefreshAds}
          disabled={isRefreshing}
          style={{ fontSize: 13 }}
        >
          {isRefreshing ? "Refreshing..." : "Refresh ads"}
        </button>
      </div>
    </header>
  );
};
