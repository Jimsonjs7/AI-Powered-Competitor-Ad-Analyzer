import React, { useState } from "react";
import { addCompetitor, crawlCompetitorWebsite, fetchDiscoveryStatus, startDiscovery } from "../api/client";
import { CompetitorCrawlResult, DiscoveryStatus } from "../types";

interface DiscoveryModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultCity: string;
  onDiscoveryStarted?: () => void;
  onCompetitorAdded?: () => void;
}

export const DiscoveryModal: React.FC<DiscoveryModalProps> = ({
  isOpen,
  onClose,
  defaultCity,
  onDiscoveryStarted,
  onCompetitorAdded,
}) => {
  const [activeTab, setActiveTab] = useState<"area_scan" | "website_crawl">("area_scan");

  // Tab 1: Area scan states
  const [city, setCity] = useState(defaultCity || "Coimbatore");
  const [selectedAreas, setSelectedAreas] = useState<string[]>(["Gandhipuram", "RS Puram", "Peelamedu"]);
  const [newAreaInput, setNewAreaInput] = useState("");
  const [selectedDomains, setSelectedDomains] = useState<string[]>([
    "Digital marketing",
    "Paid ads",
    "SEO",
    "AI",
  ]);
  const [customKeyword, setCustomKeyword] = useState("");
  const [radiusKm, setRadiusKm] = useState(15);
  const [isScanning, setIsScanning] = useState(false);
  const [scanStatus, setScanStatus] = useState<DiscoveryStatus | null>(null);
  const [scanMsg, setScanMsg] = useState("");

  // Tab 2: Website crawl states
  const [crawlUrl, setCrawlUrl] = useState("");
  const [isCrawling, setIsCrawling] = useState(false);
  const [crawlError, setCrawlError] = useState("");
  const [crawlResult, setCrawlResult] = useState<CompetitorCrawlResult | null>(null);

  // Form states for verifying crawled competitor
  const [compName, setCompName] = useState("");
  const [compCourse, setCompCourse] = useState("Digital marketing");
  const [compCity, setCompCity] = useState("Coimbatore");
  const [compArea, setCompArea] = useState("");
  const [compFbPageId, setCompFbPageId] = useState("");
  const [compIgHandle, setCompIgHandle] = useState("");
  const [isSavingComp, setIsSavingComp] = useState(false);
  const [saveCompSuccess, setSaveCompSuccess] = useState("");

  if (!isOpen) return null;

  const toggleDomain = (domain: string) => {
    setSelectedDomains((prev) =>
      prev.includes(domain) ? prev.filter((d) => d !== domain) : [...prev, domain]
    );
  };

  const addAreaTag = () => {
    if (!newAreaInput.trim()) return;
    if (!selectedAreas.includes(newAreaInput.trim())) {
      setSelectedAreas([...selectedAreas, newAreaInput.trim()]);
    }
    setNewAreaInput("");
  };

  const removeAreaTag = (areaToRemove: string) => {
    setSelectedAreas(selectedAreas.filter((a) => a !== areaToRemove));
  };

  const handleStartAreaScan = async () => {
    setIsScanning(true);
    setScanMsg("Initializing competitor discovery agent...");
    try {
      const searchTerms: string[] = [];
      if (customKeyword.trim()) {
        searchTerms.push(customKeyword.trim());
      }
      for (const domain of selectedDomains) {
        for (const area of selectedAreas) {
          searchTerms.push(`${domain} ${area}`);
        }
        searchTerms.push(`${domain} institute`);
      }

      const res = await startDiscovery({
        radius_km: radiusKm,
        city,
        areas: selectedAreas,
        domains: selectedDomains,
        search_terms: searchTerms,
      });

      setScanMsg(`Agent started (Run #${res.run_id}). Monitoring active sources...`);
      onDiscoveryStarted?.();

      // Poll status for a short while
      const pollTimer = setInterval(async () => {
        try {
          const status = await fetchDiscoveryStatus(res.run_id);
          setScanStatus(status);
          if (status.status === "completed" || status.status === "failed") {
            clearInterval(pollTimer);
            setIsScanning(false);
          }
        } catch {
          clearInterval(pollTimer);
          setIsScanning(false);
        }
      }, 3000);
    } catch (err: any) {
      setScanMsg(err.message || "Failed to start discovery scan.");
      setIsScanning(false);
    }
  };

  const handleCrawlWebsite = async () => {
    if (!crawlUrl.trim()) return;
    setIsCrawling(true);
    setCrawlError("");
    setCrawlResult(null);
    setSaveCompSuccess("");

    try {
      const res = await crawlCompetitorWebsite(crawlUrl.trim());
      setCrawlResult(res);
      setCompName(res.name);
      setCompCourse(res.course || "Digital marketing");
      setCompCity(res.city || city);
      setCompArea(res.area || "");
      setCompFbPageId(res.fb_page_id || "");
      setCompIgHandle(res.ig_handle || "");
    } catch (err: any) {
      setCrawlError(err.message || "Could not crawl this website. Check domain format and retry.");
    } finally {
      setIsCrawling(false);
    }
  };

  const handleSaveCrawledCompetitor = async () => {
    if (!compName.trim()) return;
    setIsSavingComp(true);
    try {
      await addCompetitor({
        name: compName.trim(),
        city: compCity.trim(),
        course: compCourse.trim(),
        fb_page_url: compFbPageId.trim() || undefined,
      });
      setSaveCompSuccess("Competitor verified and added to directory successfully.");
      onCompetitorAdded?.();
      setTimeout(() => {
        onClose();
      }, 1200);
    } catch (err: any) {
      setCrawlError(err.message || "Failed to save competitor.");
    } finally {
      setIsSavingComp(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0,0,0,0.4)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
        zIndex: 110,
      }}
    >
      <div
        style={{
          background: "var(--surface)",
          borderRadius: 8,
          maxWidth: 680,
          width: "100%",
          maxHeight: "90vh",
          overflowY: "auto",
          padding: 24,
          display: "flex",
          flexDirection: "column",
          gap: 16,
          boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 18 }}>Find Local Competitors</h2>
            <p style={{ margin: "4px 0 0", color: "var(--muted)", fontSize: 13 }}>
              Target specific locations, domains, and Meta Ad Library advertisers.
            </p>
          </div>
          <button className="btn" onClick={onClose} style={{ padding: "4px 10px" }}>
            Close
          </button>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: "flex", gap: 8, borderBottom: "1px solid var(--line)", paddingBottom: 10 }}>
          <button
            className="fl"
            aria-pressed={activeTab === "area_scan"}
            onClick={() => setActiveTab("area_scan")}
            style={{ fontSize: 13, padding: "6px 14px" }}
          >
            Targeted Area & Domain Scan
          </button>
          <button
            className="fl"
            aria-pressed={activeTab === "website_crawl"}
            onClick={() => setActiveTab("website_crawl")}
            style={{ fontSize: 13, padding: "6px 14px" }}
          >
            Add by Competitor Website URL
          </button>
        </div>

        {/* Tab 1: Targeted Area Scan */}
        {activeTab === "area_scan" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>
                  Target City
                </label>
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>
                  Search Radius: {radiusKm} km
                </label>
                <input
                  type="range"
                  min={5}
                  max={50}
                  step={5}
                  value={radiusKm}
                  onChange={(e) => setRadiusKm(Number(e.target.value))}
                  style={{ width: "100%", marginTop: 8 }}
                />
              </div>
            </div>

            {/* Area / Neighborhood Targeter */}
            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>
                Target Neighborhoods / Localities
              </label>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
                {selectedAreas.map((area) => (
                  <span
                    key={area}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 6,
                      background: "var(--accent-soft)",
                      color: "var(--accent)",
                      fontSize: 12,
                      padding: "3px 8px",
                      borderRadius: 4,
                      fontWeight: 500,
                    }}
                  >
                    {area}
                    <button
                      onClick={() => removeAreaTag(area)}
                      style={{ border: "none", background: "transparent", cursor: "pointer", color: "var(--accent)", fontSize: 12, padding: 0 }}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>

              <div style={{ display: "flex", gap: 8 }}>
                <input
                  type="text"
                  placeholder="Add neighbourhood (e.g. Saravanampatti, Hopes College)"
                  value={newAreaInput}
                  onChange={(e) => setNewAreaInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && addAreaTag()}
                  style={{ flex: 1, padding: "7px 10px", border: "1px solid var(--line)", borderRadius: 6, fontSize: 13 }}
                />
                <button className="btn" onClick={addAreaTag} style={{ fontSize: 12 }}>
                  Add area
                </button>
              </div>
            </div>

            {/* Domains & Courses to Target */}
            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
                Target Domains & Training Categories
              </label>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {[
                  "Digital marketing",
                  "SEO",
                  "Paid ads",
                  "Social media marketing",
                  "AI",
                  "UI/UX",
                  "Full Stack",
                  "Data Science",
                ].map((d) => (
                  <button
                    key={d}
                    type="button"
                    className="fl"
                    aria-pressed={selectedDomains.includes(d)}
                    onClick={() => toggleDomain(d)}
                    style={{ fontSize: 12, padding: "4px 10px" }}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Keyword */}
            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>
                Custom Search Keyword (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. performance marketing academy or generative ai training"
                value={customKeyword}
                onChange={(e) => setCustomKeyword(e.target.value)}
                style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6, fontSize: 13 }}
              />
            </div>

            {/* Scan Status / Feedback */}
            {scanMsg && (
              <div style={{ padding: 12, background: "var(--canvas)", borderRadius: 6, fontSize: 13, color: "var(--accent)" }}>
                {scanMsg}
                {scanStatus && (
                  <div style={{ marginTop: 6, fontSize: 12, color: "var(--ink)" }}>
                    Step: {scanStatus.current_step} | Found: {scanStatus.counts?.places_found || 0} competitors | Ads checked: {scanStatus.counts?.ads_collected || 0}
                  </div>
                )}
              </div>
            )}

            <button
              className="btn pri"
              disabled={isScanning || selectedDomains.length === 0}
              onClick={handleStartAreaScan}
              style={{ padding: "10px 16px", fontSize: 14 }}
            >
              {isScanning ? "Scanning area sources..." : "Start Competitor Discovery Scan"}
            </button>
          </div>
        )}

        {/* Tab 2: Add by Website URL Crawler */}
        {activeTab === "website_crawl" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <p style={{ margin: 0, fontSize: 13, color: "var(--muted)" }}>
              Paste a competitor's website URL. The crawler will inspect their site, extract their brand name, course offerings, and find their public Facebook & Instagram links so you can verify before saving.
            </p>

            <div style={{ display: "flex", gap: 8 }}>
              <input
                type="text"
                placeholder="https://competitor-academy.com"
                value={crawlUrl}
                onChange={(e) => setCrawlUrl(e.target.value)}
                style={{ flex: 1, padding: "8px 12px", border: "1px solid var(--line)", borderRadius: 6 }}
              />
              <button
                className="btn pri"
                disabled={isCrawling || !crawlUrl.trim()}
                onClick={handleCrawlWebsite}
              >
                {isCrawling ? "Crawling..." : "Crawl & Extract"}
              </button>
            </div>

            {crawlError && (
              <div style={{ fontSize: 13, color: "var(--danger)", padding: "8px 12px", background: "var(--danger-soft)", borderRadius: 6 }}>
                {crawlError}
              </div>
            )}

            {/* Verification Form Card */}
            {crawlResult && (
              <div
                style={{
                  background: "var(--canvas)",
                  border: "1px solid var(--line)",
                  borderRadius: 8,
                  padding: 16,
                  display: "flex",
                  flexDirection: "column",
                  gap: 12,
                }}
              >
                <h4 style={{ margin: 0, fontSize: 14 }}>Verify Extracted Details Before Adding</h4>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  <div>
                    <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 2 }}>
                      Competitor Name
                    </label>
                    <input
                      type="text"
                      value={compName}
                      onChange={(e) => setCompName(e.target.value)}
                      style={{ width: "100%", padding: "6px 8px", border: "1px solid var(--line)", borderRadius: 6, fontSize: 13 }}
                    />
                  </div>

                  <div>
                    <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 2 }}>
                      Primary Course / Domain
                    </label>
                    <select
                      value={compCourse}
                      onChange={(e) => setCompCourse(e.target.value)}
                      style={{ width: "100%", padding: "6px 8px", border: "1px solid var(--line)", borderRadius: 6, fontSize: 13 }}
                    >
                      <option value="Digital marketing">Digital marketing</option>
                      <option value="AI">AI / Machine Learning</option>
                      <option value="UI/UX">UI/UX Design</option>
                      <option value="Full Stack">Full Stack Development</option>
                      <option value="Data Science">Data Science</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 2 }}>
                      City
                    </label>
                    <input
                      type="text"
                      value={compCity}
                      onChange={(e) => setCompCity(e.target.value)}
                      style={{ width: "100%", padding: "6px 8px", border: "1px solid var(--line)", borderRadius: 6, fontSize: 13 }}
                    />
                  </div>

                  <div>
                    <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 2 }}>
                      Area / Locality
                    </label>
                    <input
                      type="text"
                      value={compArea}
                      placeholder="e.g. Peelamedu"
                      onChange={(e) => setCompArea(e.target.value)}
                      style={{ width: "100%", padding: "6px 8px", border: "1px solid var(--line)", borderRadius: 6, fontSize: 13 }}
                    />
                  </div>

                  <div>
                    <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 2 }}>
                      Facebook Page ID or URL
                    </label>
                    <input
                      type="text"
                      value={compFbPageId}
                      placeholder="Page ID or link"
                      onChange={(e) => setCompFbPageId(e.target.value)}
                      style={{ width: "100%", padding: "6px 8px", border: "1px solid var(--line)", borderRadius: 6, fontSize: 13 }}
                    />
                  </div>

                  <div>
                    <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 2 }}>
                      Instagram Handle
                    </label>
                    <input
                      type="text"
                      value={compIgHandle}
                      placeholder="@handle"
                      onChange={(e) => setCompIgHandle(e.target.value)}
                      style={{ width: "100%", padding: "6px 8px", border: "1px solid var(--line)", borderRadius: 6, fontSize: 13 }}
                    />
                  </div>
                </div>

                {crawlResult.detected_social_links.length > 0 && (
                  <div style={{ fontSize: 11, color: "var(--muted)" }}>
                    Found {crawlResult.detected_social_links.length} social profile links on their website.
                  </div>
                )}

                {saveCompSuccess && (
                  <div style={{ fontSize: 13, color: "var(--accent)", fontWeight: 500 }}>
                    {saveCompSuccess}
                  </div>
                )}

                <button
                  className="btn pri"
                  disabled={isSavingComp || !compName.trim()}
                  onClick={handleSaveCrawledCompetitor}
                  style={{ alignSelf: "flex-end", marginTop: 4 }}
                >
                  {isSavingComp ? "Adding..." : "Confirm & Add Competitor"}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

