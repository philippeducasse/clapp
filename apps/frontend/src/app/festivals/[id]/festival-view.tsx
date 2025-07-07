"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Festival } from "@/interfaces/festival";

// This is the client-side view component.
// It receives the festival data as a prop.
const FestivalView = ({ festival }: { festival: Festival }) => {
  console.log("festival", festival);
  return (
    <Card>
      <CardHeader>
        <CardTitle>{festival.festivalName}</CardTitle>
        <CardDescription>{festival.country || "No description available."}</CardDescription>
      </CardHeader>
      <CardContent>
        <p>More festival details can be displayed here.</p>
      </CardContent>
      <CardFooter>
        <p>Footer for the festival card.</p>
      </CardFooter>
    </Card>
  );
};

export default FestivalView;
