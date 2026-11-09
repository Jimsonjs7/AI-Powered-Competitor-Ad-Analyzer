import React, { useEffect, useState } from "react";
import {
  autofillProfile,
  fetchProfile,
  fetchProfileCompleteness,
  updateProfile,
} from "../api/client";
import { BusinessProfile, ProfileClaimItem, ProfileCompleteness, ProfileServiceItem } from "../types";

interface ProfileViewProps {
  onBack: () => void;
  onProfileUpdated?: () => void;
}

export const ProfileView: React.FC<ProfileViewProps> = ({ onBack, onProfileUpdated }) => {
  const [profile, setProfile] = useState<BusinessProfile | null>(null);
  const [completeness, setCompleteness] = useState<ProfileCompleteness | null>(null);
  const [activeTab, setActiveTab] = useState<"identity" | "offer" | "location" | "claims" | "online">("identity");
  const [statusMsg, setStatusMsg] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [autofillUrl, setAutofillUrl] = useState("");
  const [isAutofilling, setIsAutofilling] = useState(false);

  // Form states
  const [name, setName] = useState("");
  const [tagline, setTagline] = useState("");
  const [description, setDescription] = useState("");
  const [city, setCity] = useState("Coimbatore");
  const [area, setArea] = useState("");
  const [radiusKm, setRadiusKm] = useState(10);
  const [website, setWebsite] = useState("");
  const [facebookUrl, setFacebookUrl] = useState("");
  const [instagramUrl, setInstagramUrl] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [domainsStr, setDomainsStr] = useState("AI, Digital marketing, UI/UX");
  const [preferredCta, setPreferredCta] = useState("Book a free demo");

  // Services list
  const [services, setServices] = useState<ProfileServiceItem[]>([]);
  // Claims list
  const [claims, setClaims] = useState<ProfileClaimItem[]>([]);

  // New item inputs
  const [newServiceName, setNewServiceName] = useState("");
  const [newServiceFee, setNewServiceFee] = useState<number>(30000);
  const [newServiceDuration, setNewServiceDuration] = useState("12 weeks");
  const [newClaimText, setNewClaimText] = useState("");
  const [newClaimLink, setNewClaimLink] = useState("");

  const loadData = () => {
    fetchProfile().then((p) => {
      setProfile(p);
      setName(p.name);
      setTagline(p.tagline || "");
      setDescription(p.description || "");
      setCity(p.city);
      setArea(p.area || "");
      setRadiusKm(p.radius_km || 10);
      setWebsite(p.website || "");
      const fb = (p.social_accounts || []).find((s) => s.platform.toLowerCase() === "facebook");
      if (fb) setFacebookUrl(fb.url_or_handle);
      const ig = (p.social_accounts || []).find((s) => s.platform.toLowerCase() === "instagram");
      if (ig) setInstagramUrl(ig.url_or_handle);
      const li = (p.social_accounts || []).find((s) => s.platform.toLowerCase() === "linkedin");
      if (li) setLinkedinUrl(li.url_or_handle);
      const yt = (p.social_accounts || []).find((s) => s.platform.toLowerCase() === "youtube");
      if (yt) setYoutubeUrl(yt.url_or_handle);
      setDomainsStr((p.domains || []).join(", "));
      setPreferredCta(p.preferred_cta || "Book a free demo");
      setServices(p.services || []);
      setClaims(p.claims || []);
    });

    fetchProfileCompleteness().then(setCompleteness);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    setStatusMsg("");
    try {
      const domainsArr = domainsStr.split(",").map((s) => s.trim()).filter(Boolean);
      const socialAccountsPayload = [
        ...(facebookUrl.trim() ? [{ platform: "facebook", url_or_handle: facebookUrl.trim(), verified: true }] : []),
        ...(instagramUrl.trim() ? [{ platform: "instagram", url_or_handle: instagramUrl.trim(), verified: true }] : []),
        ...(linkedinUrl.trim() ? [{ platform: "linkedin", url_or_handle: linkedinUrl.trim(), verified: true }] : []),
        ...(youtubeUrl.trim() ? [{ platform: "youtube", url_or_handle: youtubeUrl.trim(), verified: true }] : []),
      ];
      await updateProfile({
        name,
        tagline,
        description,
        city,
        area,
        radius_km: radiusKm,
        website,
        domains: domainsArr,
        preferred_cta: preferredCta,
        services,
        claims,
        social_accounts: socialAccountsPayload,
      });
      setStatusMsg("Profile saved successfully.");
      loadData();
      onProfileUpdated?.();
    } catch (err) {
      setStatusMsg("Failed to save profile. Check values and retry.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAutofill = async () => {
    if (!autofillUrl.trim()) return;
    setIsAutofilling(true);
    setStatusMsg("");
    try {
      const res = await autofillProfile(autofillUrl.trim());
      for (const s of res.suggestions) {
        if (s.field === "name") setName(s.suggested_value);
        if (s.field === "tagline") setTagline(s.suggested_value);
        if (s.field === "description") setDescription(s.suggested_value);
        if (s.field === "domains") setDomainsStr(s.suggested_value);
        if (s.field === "city") setCity(s.suggested_value);
        if (s.field === "social_facebook") setFacebookUrl(s.suggested_value);
        if (s.field === "social_instagram") setInstagramUrl(s.suggested_value);
        if (s.field === "social_linkedin") setLinkedinUrl(s.suggested_value);
        if (s.field === "social_youtube") setYoutubeUrl(s.suggested_value);
      }
      setWebsite(autofillUrl.trim());
      setStatusMsg(`Found ${res.suggestions.length} suggestions from website.`);
    } catch (err: any) {
      setStatusMsg(err?.message || "Could not fetch details from that URL. Check domain and retry.");
    } finally {
      setIsAutofilling(false);
    }
  };

  const addService = () => {
    if (!newServiceName.trim()) return;
    setServices([
      ...services,
      {
        name: newServiceName.trim(),
        fee_min: newServiceFee,
        fee_max: newServiceFee,
        duration: newServiceDuration,
        mode: "hybrid",
      },
    ]);
    setNewServiceName("");
  };

  const removeService = (idx: number) => {
    setServices(services.filter((_, i) => i !== idx));
  };

  const addClaim = () => {
    if (!newClaimText.trim()) return;
    setClaims([
      ...claims,
      {
        text: newClaimText.trim(),
        proof_link: newClaimLink.trim() || undefined,
        approved: true,
      },
    ]);
    setNewClaimText("");
    setNewClaimLink("");
  };

  const toggleClaimApproval = (idx: number) => {
    setClaims(
      claims.map((c, i) => (i === idx ? { ...c, approved: !c.approved } : c))
    );
  };

  const removeClaim = (idx: number) => {
    setClaims(claims.filter((_, i) => i !== idx));
  };

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "24px 20px", display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Top Completeness Header */}
      <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, padding: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 18 }}>
              Business Profile & Claims Guardrail{" "}
              {profile && <span style={{ fontSize: 12, color: "var(--muted)", fontWeight: 400 }}>v{profile.version}</span>}
            </h2>
            <p style={{ margin: "4px 0 0", color: "var(--muted)", fontSize: 13 }}>
              The competitor agent and AI draft engine strictly respect your profile and approved facts.
            </p>
          </div>
          <button className="btn" onClick={onBack}>
            Back to workspace
          </button>
        </div>

        {completeness && (
          <div style={{ marginTop: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
              <span>Profile completeness</span>
              <b>{completeness.score}%</b>
            </div>
            <div style={{ height: 6, background: "var(--line)", borderRadius: 3, overflow: "hidden" }}>
              <div
                style={{
                  height: "100%",
                  width: `${completeness.score}%`,
                  background: completeness.score >= 70 ? "var(--accent)" : "var(--warn)",
                  transition: "width 0.3s ease",
                }}
              />
            </div>

            {completeness.missing_fields.length > 0 && (
              <div style={{ marginTop: 8, display: "flex", flexWrap: "wrap", gap: 6 }}>
                {completeness.missing_fields.map((h, i) => (
                  <span key={i} className="chip" style={{ fontSize: 11, background: "var(--warn-soft)", color: "var(--warn)" }}>
                    {h.field}: {h.hint}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Navigation tabs */}
      <div style={{ display: "flex", gap: 8, borderBottom: "1px solid var(--line)", paddingBottom: 8 }}>
        {(
          [
            ["identity", "Identity"],
            ["offer", "Courses & Services"],
            ["claims", "Approved Claims"],
            ["location", "Location & Radius"],
            ["online", "Online Presence"],
          ] as const
        ).map(([tabKey, label]) => (
          <button
            key={tabKey}
            className="fl"
            aria-pressed={activeTab === tabKey}
            onClick={() => setActiveTab(tabKey)}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Tab 1: Identity */}
      {activeTab === "identity" && (
        <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
          <div>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Business name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Tagline</label>
            <input
              type="text"
              value={tagline}
              placeholder="e.g. Practical AI & Digital Skills Academy"
              onChange={(e) => setTagline(e.target.value)}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Domains of work (comma-separated)</label>
            <input
              type="text"
              value={domainsStr}
              placeholder="AI, Digital marketing, UI/UX"
              onChange={(e) => setDomainsStr(e.target.value)}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Description</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Preferred Call to Action</label>
            <input
              type="text"
              value={preferredCta}
              onChange={(e) => setPreferredCta(e.target.value)}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
          </div>
        </div>
      )}

      {/* Tab 2: Courses & Services */}
      {activeTab === "offer" && (
        <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
          <h3 style={{ margin: 0, fontSize: 15 }}>Your Course Catalogue</h3>
          <p style={{ margin: "0 0 10px", color: "var(--muted)", fontSize: 13 }}>
            The AI compares your syllabus and price range against competitor ad offerings.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {services.map((s, idx) => (
              <div
                key={idx}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "10px 12px",
                  border: "1px solid var(--line)",
                  borderRadius: 6,
                }}
              >
                <div>
                  <b>{s.name}</b>
                  <div style={{ fontSize: 12, color: "var(--muted)" }}>
                    {s.duration} | Approx fee: ₹{s.fee_min?.toLocaleString()} | Mode: {s.mode}
                  </div>
                </div>
                <button className="btn" onClick={() => removeService(idx)}>
                  Remove
                </button>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
            <input
              type="text"
              placeholder="Course name (e.g. Generative AI Engineering)"
              value={newServiceName}
              onChange={(e) => setNewServiceName(e.target.value)}
              style={{ flex: "2 1 200px", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
            <input
              type="number"
              placeholder="Fee in ₹"
              value={newServiceFee}
              onChange={(e) => setNewServiceFee(Number(e.target.value))}
              style={{ flex: "1 1 100px", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
            <input
              type="text"
              placeholder="Duration"
              value={newServiceDuration}
              onChange={(e) => setNewServiceDuration(e.target.value)}
              style={{ flex: "1 1 100px", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
            <button className="btn pri" onClick={addService}>
              Add course
            </button>
          </div>
        </div>
      )}

      {/* Tab 3: Approved Claims */}
      {activeTab === "claims" && (
        <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
          <h3 style={{ margin: 0, fontSize: 15 }}>Approved Claims (Hard Guardrail)</h3>
          <p style={{ margin: "0 0 10px", color: "var(--muted)", fontSize: 13 }}>
            The AI is strictly restricted to these verified facts when drafting counter-ads.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {claims.map((c, idx) => (
              <div
                key={idx}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "10px 12px",
                  border: "1px solid var(--line)",
                  borderRadius: 6,
                  background: c.approved ? "var(--surface)" : "var(--warn-soft)",
                }}
              >
                <div style={{ flex: 1, marginRight: 10 }}>
                  <div style={{ fontWeight: 500 }}>{c.text}</div>
                  {c.proof_link && (
                    <a href={c.proof_link} target="_blank" rel="noreferrer" style={{ fontSize: 11, color: "var(--accent)" }}>
                      Proof link
                    </a>
                  )}
                </div>
                <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                  <button className="btn" onClick={() => toggleClaimApproval(idx)}>
                    {c.approved ? "Approved" : "Unapproved"}
                  </button>
                  <button className="btn" onClick={() => removeClaim(idx)}>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 8, marginTop: 10, flexDirection: "column" }}>
            <input
              type="text"
              placeholder="e.g. 100% upfront transparent fee with zero extra exam charges"
              value={newClaimText}
              onChange={(e) => setNewClaimText(e.target.value)}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
            <div style={{ display: "flex", gap: 8 }}>
              <input
                type="text"
                placeholder="Proof URL (optional)"
                value={newClaimLink}
                onChange={(e) => setNewClaimLink(e.target.value)}
                style={{ flex: 1, padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
              />
              <button className="btn pri" onClick={addClaim}>
                Add claim
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Location */}
      {activeTab === "location" && (
        <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
          <h3 style={{ margin: 0, fontSize: 15 }}>Location & Service Radius</h3>
          <p style={{ margin: "0 0 10px", color: "var(--muted)", fontSize: 13 }}>
            Sets the boundary for local competitor discovery.
          </p>

          <div>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>City</label>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Area / Neighbourhood</label>
            <input
              type="text"
              value={area}
              placeholder="e.g. Gandhipuram / RS Puram"
              onChange={(e) => setArea(e.target.value)}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Service Radius Presets</label>
            <div style={{ display: "flex", gap: 8 }}>
              {[5, 10, 25, 50].map((r) => (
                <button
                  key={r}
                  className="fl"
                  aria-pressed={radiusKm === r}
                  onClick={() => setRadiusKm(r)}
                >
                  {r} km
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Online Presence */}
      {activeTab === "online" && (
        <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
          <h3 style={{ margin: 0, fontSize: 15 }}>Online Presence & Auto-fill</h3>

          <div>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Website URL</label>
            <input
              type="text"
              placeholder="https://brandmonkconsulting.com/"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Facebook page URL</label>
              <input
                type="text"
                placeholder="https://www.facebook.com/BrandMonkconsulting/"
                value={facebookUrl}
                onChange={(e) => setFacebookUrl(e.target.value)}
                style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Instagram profile URL</label>
              <input
                type="text"
                placeholder="https://www.instagram.com/brandmonkconsulting/"
                value={instagramUrl}
                onChange={(e) => setInstagramUrl(e.target.value)}
                style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>LinkedIn company URL</label>
              <input
                type="text"
                placeholder="https://in.linkedin.com/company/brandmonkconsulting"
                value={linkedinUrl}
                onChange={(e) => setLinkedinUrl(e.target.value)}
                style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>YouTube channel URL</label>
              <input
                type="text"
                placeholder="https://www.youtube.com/channel/..."
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
              />
            </div>
          </div>

          <div style={{ marginTop: 10, padding: 14, background: "var(--canvas)", borderRadius: 6 }}>
            <h4 style={{ margin: "0 0 6px", fontSize: 14 }}>Auto-fill from website</h4>
            <p style={{ margin: "0 0 10px", color: "var(--muted)", fontSize: 12 }}>
              Crawl your institute website to extract course names and public social links. Nothing is saved without your approval.
            </p>
            <div style={{ display: "flex", gap: 8 }}>
              <input
                type="text"
                placeholder="https://yourwebsite.com"
                value={autofillUrl}
                onChange={(e) => setAutofillUrl(e.target.value)}
                style={{ flex: 1, padding: "8px 10px", border: "1px solid var(--line)", borderRadius: 6 }}
              />
              <button className="btn" disabled={isAutofilling} onClick={handleAutofill}>
                {isAutofilling ? "Crawling..." : "Auto-fill"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Action Bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 13, color: "var(--muted)" }}>{statusMsg}</span>
        <button className="btn pri" disabled={isSaving} onClick={handleSave}>
          {isSaving ? "Saving..." : "Save profile"}
        </button>
      </div>
    </div>
  );
};
