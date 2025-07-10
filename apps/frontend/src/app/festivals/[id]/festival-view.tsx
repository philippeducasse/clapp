"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import festivalApiService from "@/api/festivalApiService";
import { useFestival } from "@/context/FestivalContext";

const FestivalView = () => {
  const festival = useFestival();

  const handleUpdate = async () => {
    const response = await festivalApiService.enrichFestival(festival);

    console.log("response:", response);
  };

  return (
    <Card className="max-w-3xl mx-auto mt-6">
      <CardHeader>
        <CardTitle>{festival.festivalName}</CardTitle>
        <CardDescription>{festival.country}</CardDescription>
      </CardHeader>
      <CardContent>
        <p>
          Website:{" "}
          <Link href={festival.websiteUrl ?? "#"} target="_blank" className="underline">
            <Button variant="link">{festival.websiteUrl}</Button>
          </Link>
        </p>
        <p>Approximate date : {festival.approximateDate}</p>
        {/* <p>start date : {festival.startDate?.getDate()}</p>
        <p>end date : {festival.endDate?.getDate()}</p> */}
        <p>description : {festival.description}</p>
        <p>contact email : {festival.contactEmail}</p>
        <p>contact person : {festival.contactPerson}</p>
        <p>application start: {festival.applicationStart}</p>
        <p>application end: {festival.applicationEnd}</p>

        <Button variant="secondary" onClick={handleUpdate}>
          {" "}
          Update
        </Button>
        <Link href={`/festivals/${festival.id}/edit`}>Edit</Link>
      </CardContent>
      <CardFooter>
        <p>Footer for the festival card.</p>
      </CardFooter>
    </Card>
  );
};

export default FestivalView;
