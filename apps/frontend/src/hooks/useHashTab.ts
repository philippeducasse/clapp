import { useState, useEffect } from "react";

/**
 * Custom hook to manage tab state based on URL hash
 * @param defaultTab - The default tab to use if no hash is present
 * @returns An object containing the active tab and a function to change tabs
 */
export const useHashTab = (defaultTab: string) => {
  const [activeTab, setActiveTab] = useState(defaultTab);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const hash = window.location.hash.replace("#", "");
      if (hash) {
        setActiveTab(hash);
      }
    }
  }, []);

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    if (typeof window !== "undefined") {
      window.history.replaceState(null, "", `#${value}`);
    }
  };

  return { activeTab, handleTabChange };
};
