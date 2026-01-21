"use client";
import { useEffect, useState } from "react";
import { Progress } from "../ui/progress";
import { cn } from "@/lib/utils";
import { Flag, University, Theater, Bot, PartyPopper, CheckCircle2 } from "lucide-react";

const ICONS = [Flag, University, Theater, Bot, PartyPopper];

const DynamicProgress = ({
  className,
  value,
  ...props
}: React.ComponentProps<typeof Progress> & { value?: number }) => {
  const [internalValue, setInternalValue] = useState(0);
  const [iconIndex, setIconIndex] = useState(0);

  useEffect(() => {
    // Icon rotation every 1.5 seconds
    const iconInterval = setInterval(() => {
      setIconIndex((prev) => (prev + 1) % ICONS.length);
    }, 1500);

    let stepCount = 0;
    const progressInterval = setInterval(() => {
      setInternalValue((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        const progressRatio = stepCount / 150;
        const easing = 1 / (1 + Math.exp(-6 * progressRatio + 3));
        const baseIncrement = 100 / 150;
        const easedIncrement = baseIncrement * (0.5 + easing);
        const randomness = (Math.random() - 0.5) * baseIncrement;
        const next = Math.min(100, prev + easedIncrement + randomness);
        stepCount++;
        return next;
      });
    }, 100);

    return () => {
      clearInterval(iconInterval);
      clearInterval(progressInterval);
    };
  }, []);

  const progressValue = typeof value === "number" ? value : internalValue;
  const CurrentIcon = progressValue >= 100 ? CheckCircle2 : ICONS[iconIndex];

  return (
    <div className="flex flex-col items-center gap-4">
      <CurrentIcon
        className={cn(
          "h-12 w-12 transition-all duration-500",
          progressValue >= 100 ? "text-emerald-600 scale-110" : "text-emerald-500 animate-pulse",
        )}
      />
      <Progress value={progressValue} className={cn(className, "")} {...props} />
    </div>
  );
};

export { DynamicProgress };
