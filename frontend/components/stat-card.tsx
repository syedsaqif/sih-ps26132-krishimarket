import React from "react";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

export interface StatCardProps {
  /** The small uppercase label / title displayed at the top */
  label: string;
  /** The main stat metric (e.g. 1, ₹300, ₹2,673.82, 13.2%) */
  value: React.ReactNode;
  /** Optional icon displayed alongside the label */
  icon?: LucideIcon;
  /** Optional supporting text or status badge below the value */
  supportingText?: React.ReactNode;
  /** Optional trend or delta display */
  trend?: {
    value: string | number;
    isUp?: boolean;
    label?: string;
  };
  /** Additional styling on the value (e.g., text-primary, text-accent, text-amber-600) */
  valueClassName?: string;
  /** Root card classes */
  className?: string;
  /** Badge / status element in top right or bottom */
  badge?: React.ReactNode;
  /** Optional click handler */
  onClick?: () => void;
}

export function StatCard({
  label,
  value,
  icon: Icon,
  supportingText,
  trend,
  valueClassName,
  className,
  badge,
  onClick,
}: StatCardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "group relative flex min-h-[110px] flex-col justify-between rounded-xl border border-border/60 bg-card p-5 sm:p-6 shadow-sm transition-all duration-150 hover:shadow-md hover:border-border",
        onClick && "cursor-pointer hover:-translate-y-0.5",
        className
      )}
    >
      {/* ── Top row: Label + Icon + Optional Badge ──────────────── */}
      <div className="flex items-center justify-between gap-2 min-w-0">
        <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground min-w-0">
          {Icon && <Icon className="h-3.5 w-3.5 shrink-0 text-muted-foreground/80" />}
          <span className="truncate">{label}</span>
        </div>
        {badge && <div className="shrink-0">{badge}</div>}
      </div>

      {/* ── Middle: Main Value ───────────────────────────────────── */}
      <div className="mt-3 flex items-baseline gap-2 min-w-0">
        <div
          className={cn(
            "text-2xl sm:text-3xl font-bold tracking-tight text-foreground tabular-nums leading-tight truncate",
            valueClassName
          )}
        >
          {value}
        </div>
      </div>

      {/* ── Bottom: Supporting Text / Trend (if provided) ───────── */}
      {(supportingText || trend) && (
        <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          {trend && (
            <span
              className={cn(
                "inline-flex items-center font-medium",
                trend.isUp ? "text-primary" : "text-destructive"
              )}
            >
              {trend.isUp ? "↑" : "↓"} {trend.value}
              {trend.label && (
                <span className="ml-1 text-muted-foreground font-normal">
                  {trend.label}
                </span>
              )}
            </span>
          )}
          {supportingText && <span>{supportingText}</span>}
        </div>
      )}
    </div>
  );
}
