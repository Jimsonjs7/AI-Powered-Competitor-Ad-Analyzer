import React from "react";

interface TopBarProps {
  currentView: "wall" | "company" | "competitors" | "opportunities" | "profile" | "notes";
  onSelectView: (view: "wall" | "company" | "competitors" | "opportunities" | "profile" | "notes") => void;
  statusText: string;
  selectedCity: string;
  onCityChange: (city: string) => void;
  onRefreshAds: () => void;
  isRefreshing: boolean;
  completenessScore?: number;
  onOpenDiscovery: () => void;
  isDiscoveryRunning?: boolean;
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
  onOpenDiscovery,
  isDiscoveryRunning,
}) => {
  return (
    <header className="top" style={{ display: "flex", alignItems: "center", gap: 12, padding: "0 18px", borderBottom: "1px solid var(--line)", background: "var(--surface)" }}>
      <div className="brand" style={{ display: "flex", alignItems: "center", gap: 9, cursor: "pointer" }} onClick={() => onSelectView("wall")}>
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: 6,
            background: "#0a7c6e",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
          aria-hidden="true"
        >
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="12 2 2 7 12 12 22 7 12 2" />
            <polyline points="2 17 12 22 22 17" />
            <polyline points="2 12 12 17 22 12" />
          </svg>
        </div>
        <span style={{ fontWeight: 700, fontSize: 15, letterSpacing: "-0.01em", color: "var(--ink)" }}>Ad Desk</span>
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
          aria-pressed={currentView === "company"}
          onClick={() => onSelectView("company")}
          style={{ fontSize: 13, padding: "5px 10px" }}
        >
          By Company
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
          onClick={onOpenDiscovery}
          style={{ fontSize: 13, display: "flex", alignItems: "center", gap: 6 }}
        >
          {isDiscoveryRunning && (
            <span
              style={{
                width: 7,
                height: 7,
                borderRadius: "50%",
                background: "var(--accent, #15803d)",
                display: "inline-block",
              }}
            />
          )}
          Find competitors
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
