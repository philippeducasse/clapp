"use client";

import React, { useEffect } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { FestivalUpdateDialog } from "@/components/page-components/festival-page/components/update-view/FestivalUpdateDialog";
import DetailsView from "@/components/common/table/DetailsView";
import { getDetailsView } from "../../helpers/getDetailsView";
import BackButton from "@/components/common/buttons/BackButton";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { selectFestival, setFestival } from "@/redux/slices/festivalSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { useDispatch } from "react-redux";
import festivalApiService from "@/api/festivalApiService";
import { Festival } from "@/interfaces/Festival";

const FestivalView = () => {
  const params = useParams();
  const dispatch = useDispatch();
  const festivalId = Number(params.id);
  const festival = useSelector((state: RootState) => selectFestival(state, festivalId));

  useEffect(() => {
    const fetchFestival = async () => {
      try {
        console.log("id:", festivalId);
        const festival = await festivalApiService.getFestival(festivalId);
        dispatch(setFestival(festival as Festival));
      } catch (error) {
        console.error("Failed to fetch festival:", error);
      }
    };
    if (!festival) {
      fetchFestival();
    }
  }, [festivalId, festival, dispatch]);

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
