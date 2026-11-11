import React from "react";
import { DiscoveryStatus } from "../types";

interface BackgroundQueueBannerProps {
  run: DiscoveryStatus | null;
  onOpenDetails: () => void;
  onCancel: () => void;
  onDismiss: () => void;
  onViewCompetitors?: () => void;
}

export const BackgroundQueueBanner: React.FC<BackgroundQueueBannerProps> = ({
  run,
  onOpenDetails,
  onCancel,
  onDismiss,
  onViewCompetitors,
}) => {
  if (!run) return null;

  const isRunning = run.status === "running" || run.status === "pending";
  const isCompleted = run.status === "completed";
  const isFailed = run.status === "failed";
  const isCancelled = run.status === "cancelled";

  const places = run.counts?.places_found ?? 0;
  const pages = run.counts?.pages_resolved ?? 0;
  const ads = run.counts?.ads_collected ?? 0;

  return (
    <div
      role="region"
      aria-label="Background discovery queue status"
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 12,
        padding: "8px 20px",
        background: isRunning
          ? "var(--accent-soft, #f0fdf4)"
          : isCompleted
          ? "#ecfdf5"
          : isFailed
          ? "#fef2f2"
          : "var(--surface-muted, #f8fafc)",
        borderBottom: `1px solid ${
          isRunning
            ? "var(--accent, #15803d)"
            : isCompleted
            ? "#10b981"
            : isFailed
            ? "#ef4444"
            : "var(--line, #e2e8f0)"
        }`,
        fontSize: 13,
        color: "var(--ink, #0f172a)",
        transition: "all 0.2s ease-in-out",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1, minWidth: 0 }}>
        {/* Pulsing indicator when running */}
        {isRunning && (
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: "var(--accent, #15803d)",
              display: "inline-block",
              boxShadow: "0 0 0 0 rgba(21, 128, 61, 0.7)",
              animation: "pulse 1.8s infinite",
              flexShrink: 0,
            }}
          />
        )}

        <div style={{ display: "flex", alignItems: "baseline", gap: 8, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          <strong style={{ fontWeight: 600, color: isFailed ? "#b91c1c" : "var(--accent, #15803d)", flexShrink: 0 }}>
            {isRunning && `Background task (Run #${run.run_id}):`}
            {isCompleted && `Discovery completed (Run #${run.run_id}):`}
            {isFailed && `Discovery failed (Run #${run.run_id}):`}
            {isCancelled && `Discovery cancelled:`}
          </strong>

          <span style={{ color: "var(--ink-muted, #475569)", textOverflow: "ellipsis", overflow: "hidden" }}>
            {run.current_step || (isRunning ? "Scanning Ad Library..." : "Task finished.")}
          </span>
        </div>

        {/* Live counters pill */}
        <div
          style={{
            display: "inline-flex",
            gap: 8,
            fontSize: 11,
            fontWeight: 500,
            color: "var(--ink, #0f172a)",
            background: "rgba(255, 255, 255, 0.8)",
            padding: "2px 8px",
            borderRadius: 12,
            border: "1px solid var(--line, #e2e8f0)",
            marginLeft: 8,
            flexShrink: 0,
          }}
        >
          <span>Advertisers: <b>{places}</b></span>
          <span>·</span>
          <span>Competitors: <b>{pages}</b></span>
          <span>·</span>
          <span>Ads: <b>{ads}</b></span>
        </div>
      </div>

      {/* Action buttons */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
        {isRunning && (
          <>
            <button
              onClick={onOpenDetails}
              className="btn"
              style={{
                fontSize: 12,
                padding: "4px 10px",
                height: 28,
                background: "#fff",
              }}
            >
              View details
            </button>
            <button
              onClick={onCancel}
              style={{
                fontSize: 12,
                padding: "4px 8px",
                height: 28,
                background: "transparent",
                border: "1px solid #fca5a5",
                color: "#b91c1c",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              Cancel scan
            </button>
          </>
        )}

        {isCompleted && (
          <>
            {onViewCompetitors && (
              <button
                onClick={onViewCompetitors}
                className="btn pri"
                style={{
                  fontSize: 12,
                  padding: "4px 10px",
                  height: 28,
                }}
              >
                View competitors
              </button>
            )}
            <button
              onClick={onDismiss}
              aria-label="Dismiss completed notification"
              style={{
                background: "transparent",
                border: "none",
                fontSize: 16,
                cursor: "pointer",
                color: "var(--ink-muted, #64748b)",
                padding: "2px 6px",
              }}
            >
              ✕
            </button>
          </>
        )}

        {(isFailed || isCancelled) && (
          <button
            onClick={onDismiss}
            aria-label="Dismiss notification"
            style={{
              background: "transparent",
              border: "none",
              fontSize: 16,
              cursor: "pointer",
              color: "var(--ink-muted, #64748b)",
              padding: "2px 6px",
            }}
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
};

