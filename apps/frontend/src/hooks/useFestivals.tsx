"use client";

import { useEffect, useState } from "react";

const useFestivals = () => {
  const [festivals, setFestivals] = useState();

  useEffect(() => {
    const fetchFestivals = async () => {
      try {
        const data = await fetch("http://localhost:8000/api/festivals/");
        const festivals = await data.json();

        setFestivals(festivals);
      } catch (error) {
        console.error(`Error fetching festivals: ${error}`);
      }
    };
    fetchFestivals();
  }, []);

  return festivals;
};

export default useFestivals;
