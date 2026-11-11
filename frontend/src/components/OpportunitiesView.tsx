import React, { useEffect, useState } from "react";
import { draftOpportunityAd, fetchOpportunities } from "../api/client";
import { OpportunityDraft, OpportunityItem } from "../types";

interface OpportunitiesViewProps {
  onBack: () => void;
}

export const OpportunitiesView: React.FC<OpportunitiesViewProps> = ({ onBack }) => {
  const [opportunities, setOpportunities] = useState<OpportunityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [draftingId, setDraftingId] = useState<number | null>(null);
  const [activeDraft, setActiveDraft] = useState<OpportunityDraft | null>(null);

  const loadData = () => {
    setLoading(true);
    fetchOpportunities()
      .then((data) => {
        setOpportunities(data);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDraft = async (oppId: number) => {
    setDraftingId(oppId);
    try {
      const res = await draftOpportunityAd(oppId);
      setActiveDraft(res);
    } catch (err) {
      console.error("Draft generation failed:", err);
    } finally {
      setDraftingId(null);
    }
  };

  return (
    <div style={{ maxWidth: 1040, margin: "0 auto", padding: "24px 20px", display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 18 }}>Opportunity Engine: Counter-Ad Angles</h2>
          <p style={{ margin: "4px 0 0", color: "var(--muted)", fontSize: 13 }}>
            Ranked market-wide objections turned into approved BrandMonk counter-ads.
          </p>
        </div>
        <button className="btn" onClick={onBack}>
          Back to workspace
        </button>
      </div>

      {loading ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {[1, 2, 3].map((idx) => (
            <div
              key={idx}
              style={{
                background: "var(--surface)",
                border: "1px solid var(--line)",
                borderRadius: 8,
                padding: 18,
                display: "flex",
                flexDirection: "column",
                gap: 12,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1 }}>
                  <div style={{ display: "flex", gap: 8 }}>
                    <div className="skeleton" style={{ width: 70, height: 22, borderRadius: 12 }} />
                    <div className="skeleton" style={{ width: 110, height: 22, borderRadius: 12 }} />
                  </div>
                  <div className="skeleton" style={{ width: "60%", height: 20 }} />
                </div>
                <div className="skeleton" style={{ width: 140, height: 36, borderRadius: 6 }} />
              </div>
              <div className="skeleton" style={{ width: "90%", height: 16 }} />
              <div className="skeleton" style={{ width: "40%", height: 16 }} />
            </div>
          ))}
        </div>
      ) : opportunities.length === 0 ? (
        <div style={{ padding: 40, background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, textAlign: "center" }}>
          <b>No opportunity clusters ready yet.</b>
          <p style={{ color: "var(--muted)", fontSize: 13, margin: "6px 0 0" }}>
            Run the competitor discovery agent or collect ads/reviews to discover market gaps.
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {opportunities.map((opp) => (
            <div
              key={opp.id}
              style={{
                background: "var(--surface)",
                border: "1px solid var(--line)",
                borderRadius: 8,
                padding: 18,
                display: "flex",
                flexDirection: "column",
                gap: 12,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
                    <span className="chip" style={{ background: "var(--accent-soft)", color: "var(--accent)", fontWeight: 600 }}>
                      Score {opp.score}
                    </span>
                    <span className="chip">{opp.category.replace("_", " ")}</span>
                  </div>
                  <h3 style={{ margin: 0, fontSize: 16 }}>{opp.cluster_label}</h3>
                </div>
                <button
                  className="btn pri"
                  disabled={draftingId === opp.id}
                  onClick={() => handleDraft(opp.id)}
                >
                  {draftingId === opp.id ? "Drafting..." : "Draft counter-ad"}
                </button>
              </div>

              {opp.counter_angle && (
                <p style={{ margin: 0, fontSize: 14, color: "var(--ink)", lineHeight: 1.5 }}>
                  <b>Strategic Counter-Angle:</b> {opp.counter_angle}
                </p>
              )}

              {opp.headlines && opp.headlines.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {opp.headlines.slice(0, 2).map((h, i) => (
                    <span key={i} style={{ fontSize: 12, padding: "4px 8px", background: "var(--canvas)", borderRadius: 4 }}>
                      "{h}"
                    </span>
                  ))}
                </div>
              )}

              {opp.missing_proof && opp.missing_proof.length > 0 && (
                <div style={{ padding: "8px 12px", background: "var(--warn-soft)", borderRadius: 6, fontSize: 12, color: "var(--warn)" }}>
                  <b>Proof Gap in Profile:</b> {opp.missing_proof[0]}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Draft modal/flyout */}
      {activeDraft && (
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
            zIndex: 100,
          }}
        >
          <div
            style={{
              background: "var(--surface)",
              borderRadius: 8,
              maxWidth: 580,
              width: "100%",
              padding: 24,
              display: "flex",
              flexDirection: "column",
              gap: 16,
              maxHeight: "90vh",
              overflowY: "auto",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ margin: 0, fontSize: 17 }}>Draft Counter-Ad</h3>
              <button className="btn" onClick={() => setActiveDraft(null)}>
                Close
              </button>
            </div>

            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: "var(--muted)", textTransform: "uppercase" }}>
                Headline Options (Answer-First)
              </label>
              <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 6 }}>
                {activeDraft.headline_options.map((h, i) => (
                  <div key={i} style={{ padding: "8px 10px", background: "var(--canvas)", borderRadius: 6, fontSize: 14 }}>
                    {h}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: "var(--muted)", textTransform: "uppercase" }}>
                Primary Body Text
              </label>
              <div style={{ padding: "10px 12px", border: "1px solid var(--line)", borderRadius: 6, marginTop: 6, fontSize: 14 }}>
                {activeDraft.primary_text}
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
              <span>
                <b>Call to Action:</b> {activeDraft.cta}
              </span>
              <span>
                <b>Recommended Format:</b> {activeDraft.recommended_format}
              </span>
            </div>

            {activeDraft.used_claims.length > 0 && (
              <div style={{ fontSize: 12, color: "var(--muted)" }}>
                <b>Approved Claims Enforced:</b> {activeDraft.used_claims.join("; ")}
              </div>
            )}

            <div style={{ padding: 10, background: "var(--canvas)", borderRadius: 6, fontSize: 11, color: "var(--muted)" }}>
              {activeDraft.compliance_note}
            </div>

            <button
              className="btn pri"
              onClick={() => {
                navigator.clipboard.writeText(
                  `${activeDraft.headline_options[0]}\n\n${activeDraft.primary_text}\n\nCTA: ${activeDraft.cta}`
                );
                alert("Copied to clipboard.");
              }}
            >
              Copy draft to clipboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

