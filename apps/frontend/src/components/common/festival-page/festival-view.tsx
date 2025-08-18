"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useFestival } from "@/context/FestivalContext";
import { FestivalUpdateDialog } from "@/components/common/festival-page/FestivalUpdateDialog";
import DetailsView from "@/components/common/table/DetailsView";
import { getDetailsView } from "./helpers/getDetailsView";
import BackButton from "@/components/common/buttons/BackButton";
import EditButton from "@/components/common/buttons/EditButton";

const FestivalView = () => {
  const { festival } = useFestival();

  return (
    <Card className=" mx-auto mt-6">
      <CardHeader>
        <CardTitle>{festival.festivalName}</CardTitle>
        <CardDescription>{festival.country}</CardDescription>
      </CardHeader>
      <CardContent className="grid-cols-2">
        <DetailsView data={getDetailsView(festival)} />
      </CardContent>
      <CardFooter className="gap-6">
        <FestivalUpdateDialog />
        <EditButton href={`/festivals/${festival.id}/edit`} />
        <BackButton href="/festivals" />
      </CardFooter>
    </Card>
  );
};

export default FestivalView;
