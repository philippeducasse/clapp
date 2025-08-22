"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { FestivalUpdateDialog } from "@/components/page-components/festival-page/components/update-view/FestivalUpdateDialog";
import DetailsView from "@/components/common/table/DetailsView";
import { getDetailsView } from "../../helpers/getDetailsView";
import BackButton from "@/components/common/buttons/BackButton";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { selectFestivalById } from "@/redux/slices/festivalSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";

const FestivalView = () => {
  const params = useParams();
  const festivalId = Number(params.id);
  const festival = useSelector((state: RootState) => selectFestivalById(state, festivalId));
  console.log({ festival });
  if (!festival) {
    return <div>Festival not found.</div>;
  }

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
