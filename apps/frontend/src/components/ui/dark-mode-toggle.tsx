"use client";

import React, { useState, useEffect } from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";
import { NavigationMenuContent } from "./navigation-menu";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function DarkModeToggle() {
  const { setTheme } = useTheme();
  const [mode, setMode] = useState<"dark" | "light" | "system">("system");

  const toggleMode = (mode: "dark" | "light") => {
    setMode(mode);
    setTheme(mode);
  };

  return (
    <Button
      className="cursor-pointer"
      variant="outline"
      size="icon"
      onClick={mode === "dark" ? () => toggleMode("light") : () => toggleMode("dark")}
    >
      <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
      <Moon className="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}
