import React from "react";

interface TopBarProps {
  statusText: string;
  selectedCity: string;
  onCityChange: (city: string) => void;
  showNotes: boolean;
  onToggleNotes: () => void;
  onRefreshAds: () => void;
  isRefreshing: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  statusText,
  selectedCity,
  onCityChange,
  showNotes,
  onToggleNotes,
  onRefreshAds,
  isRefreshing,
}) => {
  return (
    <header className="top">
      <div className="brand">
        <span className="mark">B</span>Ad Desk
      </div>
      <span className="src" role="status">
        <i></i>
        {statusText}
      </span>
      <select
        aria-label="City"
        value={selectedCity}
        onChange={(e) => onCityChange(e.target.value)}
      >
        <option value="Coimbatore">Coimbatore</option>
        <option value="Kochi">Kochi</option>
        <option value="Bengaluru">Bengaluru</option>
      </select>
      <button className="btn" onClick={onToggleNotes}>
        {showNotes ? "Back to workspace" : "Design notes"}
      </button>
      <button
        className="btn pri"
        onClick={onRefreshAds}
        disabled={isRefreshing}
      >
        {isRefreshing ? "Refreshing..." : "Refresh ads"}
      </button>
    </header>
  );
};

