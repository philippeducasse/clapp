"use client";

import { useEffect, useRef, useState } from "react";
import { RotateCw, Square } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DiscoveryRun } from "@/interfaces/entities/Discovery";
import {
  COUNTER_LABELS,
  RUN_STATUS_STYLES,
  runLabel,
} from "../helpers/discoveryLabels";

interface DiscoveryRunPanelProps {
  run: DiscoveryRun | null;
  runs: DiscoveryRun[];
  onSelectRun: (id: number) => void;
  onCancel: (run: DiscoveryRun) => Promise<void>;
  onRerun: (run: DiscoveryRun) => Promise<boolean>;
  rerunDisabled: boolean;
}

const formatTime = (value: string) =>
  new Date(value).toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

const DiscoveryRunPanel = ({
  run,
  runs,
  onSelectRun,
  onCancel,
  onRerun,
  rerunDisabled,
}: DiscoveryRunPanelProps) => {
  const logRef = useRef<HTMLDivElement>(null);
  const [isRerunning, setIsRerunning] = useState(false);
  const lines = run?.progress.length ?? 0;

  const handleRerun = async (target: DiscoveryRun) => {
    setIsRerunning(true);
    try {
      await onRerun(target);
    } finally {
      setIsRerunning(false);
    }
  };

  // Keep the newest progress line in view while the run is going.
  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [lines]);

  return (
    <div className="space-y-3">
      {runs.length > 0 && (
        <Select
          value={run ? run.id.toString() : undefined}
          onValueChange={(v) => onSelectRun(Number(v))}
        >
          <SelectTrigger className="w-full max-w-2xl" aria-label="Recent runs">
            <SelectValue placeholder="Recent runs" />
          </SelectTrigger>
          <SelectContent>
            {runs.map((item) => (
              <SelectItem key={item.id} value={item.id.toString()}>
                {runLabel(item)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {!run ? (
        <p className="text-muted-foreground text-sm">No discovery run yet.</p>
      ) : (
        <div className="p-3 rounded-lg border space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <Badge
                variant="outline"
                className={RUN_STATUS_STYLES[run.status]}
              >
                {run.status.toLowerCase()}
              </Badge>
              <span className="font-medium break-all">{run.startingPoint}</span>
            </div>
            {run.isActive ? (
              <Button
                size="sm"
                variant="outline"
                disabled={run.cancelRequested}
                onClick={() => onCancel(run)}
              >
                <Square /> {run.cancelRequested ? "Cancelling…" : "Cancel"}
              </Button>
            ) : (
              <Button
                size="sm"
                variant="outline"
                disabled={rerunDisabled || isRerunning}
                title={
                  rerunDisabled ? "Another discovery is running" : undefined
                }
                onClick={() => handleRerun(run)}
              >
                <RotateCw /> {isRerunning ? "Starting…" : "Run again"}
              </Button>
            )}
          </div>

          {run.plan?.goal && (
            <p className="text-sm">
              <span className="text-muted-foreground">Goal:</span>{" "}
              {run.plan.goal}
              {run.plan.queries && run.plan.queries.length > 0 && (
                <span className="text-muted-foreground">
                  {" "}
                  · searches: {run.plan.queries.join("; ")}
                </span>
              )}
            </p>
          )}

          <div className="flex flex-wrap gap-2">
            {COUNTER_LABELS.map(({ key, label }) => (
              <Badge key={key} variant="outline">
                {label}: {run.counters?.[key] ?? 0}
              </Badge>
            ))}
          </div>

          <div
            ref={logRef}
            className="max-h-72 overflow-y-auto rounded bg-muted/40 p-2 font-mono text-xs space-y-0.5"
          >
            {run.progress.length === 0 ? (
              <p className="text-muted-foreground">
                Waiting for the discovery service…
              </p>
            ) : (
              run.progress.map((line, index) => (
                <p key={index} className="break-words">
                  <span className="text-muted-foreground">
                    {formatTime(line.at)}
                  </span>{" "}
                  <span className="text-primary">[{line.step}]</span>{" "}
                  {line.message}
                </p>
              ))
            )}
          </div>

          {run.error && (
            <p className="text-sm text-red-700">Error: {run.error}</p>
          )}
          {run.errors.length > 0 && (
            <details>
              <summary className="cursor-pointer text-sm text-muted-foreground">
                Problems along the way ({run.errors.length})
              </summary>
              <ul className="mt-2 text-xs font-mono space-y-0.5">
                {run.errors.map((error, index) => (
                  <li key={index} className="break-words">
                    {error}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}
    </div>
  );
};

export default DiscoveryRunPanel;
