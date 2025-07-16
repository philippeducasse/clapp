"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { useFestival } from "@/context/FestivalContext";
import { FestivalUpdateDialog } from "@/components/common/festival-page/FestivalUpdateDialog";
import DetailsView from "@/components/common/table/DetailsView";
import { getDetailsView } from "./helpers/getDetailsView";

const FestivalView = () => {
  const festival = useFestival();

  return (
    <Card className=" mx-auto mt-6">
      <CardHeader>
        <CardTitle>{festival.festivalName}</CardTitle>
        <CardDescription>{festival.country}</CardDescription>
      </CardHeader>
      <CardContent className="grid-cols-2">
        <DetailsView data={getDetailsView(festival)} title="" />
        <FestivalUpdateDialog />
        <Link href={`/festivals/${festival.id}/edit`} className="ml-8">
          Edit
        </Link>
      </CardContent>
      <CardFooter></CardFooter>
    </Card>
  );
};

export default FestivalView;
