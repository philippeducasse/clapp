"use client";

import { useEffect, useState } from "react";
import { Festival } from "@/interfaces/Festival";
import camelcaseKeys from "camelcase-keys";

const useFestivals = () => {
  const [festivals, setFestivals] = useState<Festival[]>([]);

  useEffect(() => {
    const fetchFestivals = async () => {
      try {
        const data = await fetch("http://localhost:8000/api/festivals/");
        const json = await data.json();
        const camelized = camelcaseKeys(json, { deep: true });
        if (camelized) setFestivals(camelized);
      } catch (error) {
        console.error(`Error fetching festivals: ${error}`);
      }
    };
    fetchFestivals();
  }, []);

  return festivals;
};

export default useFestivals;
