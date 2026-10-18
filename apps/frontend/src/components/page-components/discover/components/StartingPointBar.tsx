"use client";

import { FormEvent, useState } from "react";
import { Compass } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface StartingPointBarProps {
  disabled: boolean;
  onStart: (startingPoint: string) => Promise<boolean>;
}

const StartingPointBar = ({ disabled, onStart }: StartingPointBarProps) => {
  const [value, setValue] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const startingPoint = value.trim();
    if (!startingPoint) return;
    setIsSubmitting(true);
    try {
      if (await onStart(startingPoint)) setValue("");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Paste a link, describe what to look for, or both…"
        maxLength={2000}
        aria-label="Starting point"
        className="flex-grow"
      />
      <Button type="submit" disabled={disabled || isSubmitting || !value.trim()}>
        <Compass /> Discover
      </Button>
    </form>
  );
};

export default StartingPointBar;
