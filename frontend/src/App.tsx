import React, { useEffect, useState, useCallback } from "react";
import { TopBar } from "./components/TopBar";
import { CompetitorRail } from "./components/CompetitorRail";
import { AdWall } from "./components/AdWall";
import { DetailPane } from "./components/DetailPane";
import { DesignNotes } from "./components/DesignNotes";
import { Ad, Competitor } from "./types";
import {
  addCompetitor,
  fetchAds,
  fetchCompetitors,
  fetchHealth,
  refreshAds,
} from "./api/client";

export const App: React.FC = () => {
  const [city, setCity] = useState("Coimbatore");
  const [statusText, setStatusText] = useState("All 3 ad sources responding");
  const [showNotes, setShowNotes] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [selectedCompetitorNames, setSelectedCompetitorNames] = useState<Set<string>>(
    new Set()
  );

  const [ads, setAds] = useState<Ad[]>([]);
  const [selectedCourse, setSelectedCourse] = useState("All");
  const [sortBy, setSortBy] = useState("days");
  const [selectedAdId, setSelectedAdId] = useState<number | null>(null);
  const [isPaneOpen, setIsPaneOpen] = useState(false);

  // Load initial health status
  useEffect(() => {
    fetchHealth()
      .then((h) => setStatusText(h.message))
      .catch(() => setStatusText("Ad source service active"));
  }, []);

  // Load competitors
  const loadCompetitors = useCallback(() => {
    fetchCompetitors(city)
      .then((data) => {
        setCompetitors(data);
        setSelectedCompetitorNames(new Set(data.map((c) => c.name)));
      })
      .catch((err) => {
        console.error("Failed to load competitors:", err);
      });
  }, [city]);

  useEffect(() => {
    loadCompetitors();
  }, [loadCompetitors]);

  // Load ads
  const loadAds = useCallback(() => {
    fetchAds({
      course: selectedCourse,
      sortBy: sortBy,
    })
      .then((data) => {
        // Filter by selected competitor names locally
        const filtered = data.filter((a) =>
          selectedCompetitorNames.size > 0 ? selectedCompetitorNames.has(a.competitor_name) : true
        );
        setAds(filtered);
        if (filtered.length > 0 && (!selectedAdId || !filtered.some((a) => a.id === selectedAdId))) {
          setSelectedAdId(filtered[0].id);
        }
      })
      .catch((err) => {
        console.error("Failed to load ads:", err);
      });
  }, [selectedCourse, sortBy, selectedCompetitorNames, selectedAdId]);

  useEffect(() => {
    loadAds();
  }, [loadAds]);

  const handleToggleCompetitor = (name: string, checked: boolean) => {
    setSelectedCompetitorNames((prev) => {
      const next = new Set(prev);
      if (checked) {
        next.add(name);
      } else {
        next.delete(name);
      }
      return next;
    });
  };

  const handleAddCompetitor = async (nameOrUrl: string) => {
    try {
      await addCompetitor({ name: nameOrUrl, city });
      loadCompetitors();
    } catch (err) {
      console.error("Add competitor failed:", err);
    }
  };

  const handleRefreshAds = async () => {
    setIsRefreshing(true);
    try {
      await refreshAds();
      loadAds();
    } catch (err) {
      console.error("Refresh failed:", err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleSelectAd = (id: number) => {
    setSelectedAdId(id);
    setIsPaneOpen(true);
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsPaneOpen(false);
        return;
      }

      if (/^(INPUT|TEXTAREA|SELECT)$/.test((e.target as HTMLElement).tagName)) {
        return;
      }

      const key = e.key;
      const step = ["ArrowDown", "ArrowRight", "j"].includes(key)
        ? 1
        : ["ArrowUp", "ArrowLeft", "k"].includes(key)
        ? -1
        : 0;

      if (!step || ads.length === 0) return;

      e.preventDefault();
      const currentIndex = ads.findIndex((a) => a.id === selectedAdId);
      const nextIndex = Math.max(0, Math.min(ads.length - 1, currentIndex + step));
      setSelectedAdId(ads[nextIndex].id);
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [ads, selectedAdId]);

  const selectedAd = ads.find((a) => a.id === selectedAdId) || ads[0] || null;

  return (
    <>
      <TopBar
        statusText={statusText}
        selectedCity={city}
        onCityChange={(c) => setCity(c)}
        showNotes={showNotes}
        onToggleNotes={() => setShowNotes(!showNotes)}
        onRefreshAds={handleRefreshAds}
        isRefreshing={isRefreshing}
      />

      {showNotes ? (
        <DesignNotes onBack={() => setShowNotes(false)} />
      ) : (
        <div className="shell" id="work">
          <CompetitorRail
            competitors={competitors}
            selectedNames={selectedCompetitorNames}
            onToggleCompetitor={handleToggleCompetitor}
            onAddCompetitor={handleAddCompetitor}
          />

          <AdWall
            ads={ads}
            selectedAdId={selectedAdId}
            selectedCourse={selectedCourse}
            sortBy={sortBy}
            onSelectCourse={setSelectedCourse}
            onSelectSort={setSortBy}
            onSelectAd={handleSelectAd}
          />

          <DetailPane
            ad={selectedAd}
            isOpen={isPaneOpen}
            onClose={() => setIsPaneOpen(false)}
          />
        </div>
      )}
    </>
  );
};
export default App;
