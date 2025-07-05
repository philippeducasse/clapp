"use client";
import React, { useEffect } from "react";
import useFestivals from "@/hooks/useFestivals";

const Page = () => {
  const festivals = useFestivals();
  console.log("festivals:", festivals);
  return (
    <>
      <div>Circus Agent Frontend</div>
      {festivals?.length > 0 ? (
        <ul>
          {festivals?.map((f) => (
            <li key={f.id}>{f.festival_name}</li>
          ))}
        </ul>
      ) : (
        <p>No festivals found!</p>
      )}
    </>
  );
};

export default Page;
