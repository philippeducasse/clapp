"use client";

import { useEffect, useState } from "react";
import { Progress } from "../ui/progress";
import { cn } from "@/lib/utils";

// Sigmoid easing function to simulate acceleration/deceleration
const sigmoid = (x: number): number => 1 / (1 + Math.exp(-x));

const TOTAL_DURATION_MS = 15_000;
const STEP_INTERVAL_MS = 100; // update every 100ms → 100 steps
const MAX_STEPS = TOTAL_DURATION_MS / STEP_INTERVAL_MS;

const DynamicProgress = ({
  className,
  value,
  ...props
}: React.ComponentProps<typeof Progress> & { value?: number }) => {
  const [internalValue, setInternalValue] = useState(0);

  useEffect(() => {
    let stepCount = 0;
    const interval = setInterval(() => {
      setInternalValue((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }

        const progressRatio = stepCount / MAX_STEPS;
        const easing = sigmoid(6 * progressRatio - 3); // map from 0..1 to ~0..1
        const baseIncrement = 100 / MAX_STEPS; // uniform target step
        const easedIncrement = baseIncrement * (0.5 + easing); // boost early/mid

        const randomness = (Math.random() - 0.5) * baseIncrement; // wiggle
        const next = Math.min(100, prev + easedIncrement + randomness);

        stepCount++;
        return next;
      });
    }, STEP_INTERVAL_MS);

    return () => clearInterval(interval);
  }, []);

  const progressValue = typeof value === "number" ? value : internalValue;

  return <Progress value={progressValue} className={cn(className)} {...props} />;
};

export { DynamicProgress };
