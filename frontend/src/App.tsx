import React, { useEffect, useState, useCallback } from "react";
import { TopBar } from "./components/TopBar";
import { CompetitorRail } from "./components/CompetitorRail";
import { AdWall } from "./components/AdWall";
import { DetailPane } from "./components/DetailPane";
import { DesignNotes } from "./components/DesignNotes";
import { ProfileView } from "./components/ProfileView";
import { OpportunitiesView } from "./components/OpportunitiesView";
import { CompetitorTableView } from "./components/CompetitorTableView";
import { CompanyAdView } from "./components/CompanyAdView";
import { DiscoveryModal } from "./components/DiscoveryModal";
import { BackgroundQueueBanner } from "./components/BackgroundQueueBanner";
import { Ad, Competitor, DiscoveryStatus, MarketInsight } from "./types";
import {
  addCompetitor,
  cancelDiscovery,
  fetchActiveDiscovery,
  fetchAds,
  fetchCompetitors,
  fetchDiscoveryStatus,
  fetchHealth,
  fetchMarketInsights,
  fetchProfileCompleteness,
  refreshAds,
  startDiscovery,
} from "./api/client";

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<"wall" | "company" | "competitors" | "opportunities" | "profile" | "notes">("wall");
  const [city, setCity] = useState("Coimbatore");
  const [focusedCompanyId, setFocusedCompanyId] = useState<number | null>(null);
  const [statusText, setStatusText] = useState("All 3 ad sources responding");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [completenessScore, setCompletenessScore] = useState<number>(0);
  const [isDiscoveryModalOpen, setIsDiscoveryModalOpen] = useState(false);
  const [activeDiscoveryRun, setActiveDiscoveryRun] = useState<DiscoveryStatus | null>(null);

  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [selectedCompetitorNames, setSelectedCompetitorNames] = useState<Set<string>>(
    new Set()
  );

  const [ads, setAds] = useState<Ad[]>([]);
  const [isLoadingAds, setIsLoadingAds] = useState(false);
  const [marketInsight, setMarketInsight] = useState<MarketInsight | null>(null);
  const [selectedCourse, setSelectedCourse] = useState("All");
  const [sortBy, setSortBy] = useState("days");
  const [selectedAdId, setSelectedAdId] = useState<number | null>(null);
  const [isPaneOpen, setIsPaneOpen] = useState(false);

  // Load health & profile completeness
  const loadCompleteness = () => {
    fetchProfileCompleteness()
      .then((c) => setCompletenessScore(c.score))
      .catch(() => setCompletenessScore(50));
  };

  useEffect(() => {
    fetchHealth()
      .then((h) => setStatusText(h.message))
      .catch(() => setStatusText("Ad source service active"));
    loadCompleteness();
  }, []);

  // Load competitors
  const loadCompetitors = useCallback(() => {
    fetchCompetitors({ city })
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

  // Load market insights
  const loadMarketInsights = useCallback(() => {
    fetchMarketInsights(city)
      .then((data) => {
        setMarketInsight(data);
      })
      .catch((err) => {
        console.error("Failed to load insights:", err);
      });
  }, [city]);

  useEffect(() => {
    loadMarketInsights();
  }, [loadMarketInsights]);

  // Load ads
  const loadAds = useCallback(() => {
    setIsLoadingAds(true);
    fetchAds({
      course: selectedCourse,
      sortBy: sortBy,
    })
      .then((data) => {
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
      })
      .finally(() => {
        setIsLoadingAds(false);
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
    setIsRefreshing(true);
    try {
      await addCompetitor({ name: nameOrUrl, city });
      loadCompetitors();
      loadAds();
      loadMarketInsights();
    } catch (err) {
      console.error("Add competitor failed:", err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleRefreshAds = async () => {
    setIsRefreshing(true);
    try {
      await refreshAds();
      loadCompetitors();
      loadAds();
      loadMarketInsights();
    } catch (err) {
      console.error("Refresh failed:", err);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Check for in-flight discovery run on mount
  useEffect(() => {
    fetchActiveDiscovery()
      .then((run) => {
        if (run && (run.status === "running" || run.status === "pending")) {
          setActiveDiscoveryRun(run);
        }
      })
      .catch(() => {});
  }, []);

  // Poll in-flight discovery run in background
  useEffect(() => {
    if (!activeDiscoveryRun || (activeDiscoveryRun.status !== "running" && activeDiscoveryRun.status !== "pending")) {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const status = await fetchDiscoveryStatus(activeDiscoveryRun.run_id);
        setActiveDiscoveryRun(status);
        if (status.status === "completed") {
          clearInterval(interval);
          loadCompetitors();
          loadAds();
          loadMarketInsights();
          loadCompleteness();
        } else if (status.status === "failed" || status.status === "cancelled") {
          clearInterval(interval);
        }
      } catch (err) {
        console.error("Discovery polling error:", err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [activeDiscoveryRun?.run_id, activeDiscoveryRun?.status, loadCompetitors, loadAds, loadMarketInsights]);

  const handleStartDiscovery = async (payload: {
    radius_km: number;
    city: string;
    areas: string[];
    domains: string[];
    search_terms: string[];
  }) => {
    const res = await startDiscovery(payload);
    const initialStatus: DiscoveryStatus = {
      run_id: res.run_id,
      status: "running",
      current_step: "Initializing competitor discovery agent...",
      radius_km: payload.radius_km,
      counts: { places_found: 0, pages_resolved: 0, ads_collected: 0 },
      started_at: new Date().toISOString(),
    };
    setActiveDiscoveryRun(initialStatus);
    return res.run_id;
  };

  const handleCancelDiscovery = async (runId: number) => {
    try {
      await cancelDiscovery(runId);
      setActiveDiscoveryRun((prev) =>
        prev && prev.run_id === runId
          ? { ...prev, status: "cancelled", current_step: "Scan cancelled by user" }
          : null
      );
    } catch (err) {
      console.error("Cancel discovery error:", err);
    }
  };

  const handleSelectAd = (id: number) => {
    setSelectedAdId(id);
    setIsPaneOpen(true);
  };

  // Keyboard navigation for ad wall
  useEffect(() => {
    if (currentView !== "wall") return;

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
  }, [ads, selectedAdId, currentView]);

  const selectedAd = ads.find((a) => a.id === selectedAdId) || ads[0] || null;

  return (
    <>
      <TopBar
        currentView={currentView}
        onSelectView={setCurrentView}
        statusText={statusText}
        selectedCity={city}
        onCityChange={(c) => setCity(c)}
        onRefreshAds={handleRefreshAds}
        isRefreshing={isRefreshing}
        completenessScore={completenessScore}
        onOpenDiscovery={() => setIsDiscoveryModalOpen(true)}
        isDiscoveryRunning={Boolean(
          activeDiscoveryRun &&
            (activeDiscoveryRun.status === "running" || activeDiscoveryRun.status === "pending")
        )}
      />

      <BackgroundQueueBanner
        run={activeDiscoveryRun}
        onOpenDetails={() => setIsDiscoveryModalOpen(true)}
        onCancel={() => activeDiscoveryRun && handleCancelDiscovery(activeDiscoveryRun.run_id)}
        onDismiss={() => setActiveDiscoveryRun(null)}
        onViewCompetitors={() => {
          setCurrentView("competitors");
          setActiveDiscoveryRun(null);
        }}
      />

      <DiscoveryModal
        isOpen={isDiscoveryModalOpen}
        onClose={() => setIsDiscoveryModalOpen(false)}
        defaultCity={city}
        activeRun={activeDiscoveryRun}
        onStartDiscovery={handleStartDiscovery}
        onCancelDiscovery={handleCancelDiscovery}
        onCompetitorAdded={() => {
          loadCompetitors();
          loadAds();
          loadMarketInsights();
        }}
      />

      {currentView === "profile" && (
        <ProfileView
          onBack={() => setCurrentView("wall")}
          onProfileUpdated={loadCompleteness}
        />
      )}

      {currentView === "opportunities" && (
        <OpportunitiesView onBack={() => setCurrentView("wall")} />
      )}

      {currentView === "company" && (
        <CompanyAdView
          competitors={competitors}
          ads={ads}
          initialCompanyId={focusedCompanyId}
          onBackToWall={() => setCurrentView("wall")}
          onRefreshAds={handleRefreshAds}
          isRefreshing={isRefreshing}
          onSelectAdForPoster={(ad) => {
            setSelectedAdId(ad.id);
            setCurrentView("wall");
            setIsPaneOpen(true);
          }}
        />
      )}

      {currentView === "competitors" && (
        <CompetitorTableView
          competitors={competitors}
          onBack={() => setCurrentView("wall")}
          onRefreshCompetitors={loadCompetitors}
        />
      )}

      {currentView === "notes" && (
        <DesignNotes onBack={() => setCurrentView("wall")} />
      )}

      {currentView === "wall" && (
        <div className="shell" id="work">
          <CompetitorRail
            competitors={competitors}
            selectedNames={selectedCompetitorNames}
            onToggleCompetitor={handleToggleCompetitor}
            onAddCompetitor={handleAddCompetitor}
            onViewCompanyDossier={(compId) => {
              setFocusedCompanyId(compId);
              setCurrentView("company");
            }}
          />

          <AdWall
            ads={ads}
            marketInsight={marketInsight}
            selectedAdId={selectedAdId}
            selectedCourse={selectedCourse}
            sortBy={sortBy}
            isLoading={isLoadingAds || isRefreshing}
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
