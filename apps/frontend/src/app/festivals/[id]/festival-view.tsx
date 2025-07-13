"use client";

import React, { useState } from "react";
import { createPortal } from "react-dom";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import festivalApiService from "@/api/festivalApiService";
import { useFestival } from "@/context/FestivalContext";
import { FestivalUpdateDialog } from "@/components/common/FestivalUpdateDialog";
import { DialogTrigger } from "@/components/ui/dialog";

const FestivalView = () => {
  const festival = useFestival();

  // const handleUpdate = async () => {
  //   console.log("Click", openDiffTable);
  //   setOpenDiffTable(true);
  //   setIsLoading(true);
  //   const response = await festivalApiService.enrichFestival(festival);
  //   if (response) {
  //     setIsLoading(false);
  //     setUpdatedFields(response);
  //   }
  // };

  return (
    <>
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

          <FestivalUpdateDialog />
          <Link href={`/festivals/${festival.id}/edit`} className="ml-8">
            Edit
          </Link>
        </CardContent>
        <CardFooter>
          <p>Footer for the festival card.</p>
        </CardFooter>
      </Card>
      {/* {openDiffTable &&
        createPortal(<FestivalUpdateDialog updatedFields={updatedFields} originalFields={festival} />, document.body)} */}
    </>
  );
};

export default FestivalView;
