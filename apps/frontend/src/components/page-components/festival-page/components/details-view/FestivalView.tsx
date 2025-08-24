"use client";

import React, { useEffect } from "react";
import { Speaker } from "lucide-react";
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card";
import { FestivalUpdateDialog } from "@/components/page-components/festival-page/components/update-view/FestivalUpdateDialog";
import DetailsView from "@/components/common/table/DetailsView";
import BackButton from "@/components/common/buttons/BackButton";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { selectFestival, setSelectedFestival } from "@/redux/slices/festivalSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { useDispatch } from "react-redux";
import festivalApiService from "@/api/festivalApiService";
import { getBasicFestivalInfo } from "../../helpers/getBasicFestivalInfo";
import { getFestivalDetails } from "../../helpers/getFestivalDetails";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import { useRouter } from "next/navigation";
import { Info, NotebookTabs } from "lucide-react";
import { refreshFestival } from "../../helpers/refreshFestival";
import { Skeleton } from "@/components/ui/skeleton";

const FestivalView = () => {
  const params = useParams();
  const dispatch = useDispatch();
  const festivalId = Number(params.id);
  const festival = useSelector((state: RootState) => selectFestival(state, festivalId));
  const router = useRouter();

  useEffect(() => {
    if (!festival) {
      refreshFestival(festivalId, dispatch);
    } else {
      dispatch(setSelectedFestival(festival));
    }
  }, [festivalId, festival, dispatch]);

  if (!festival) {
    return <Skeleton />;
  }

  const goToApplication = () => {
    router.push("/applications");
  };

  return (
    <div className="flex flex-col max-w-6xl mx-auto">
      <div className="flex justify-between my-6">
        <div className="flex items-center gap-2">
          <Speaker className="text-emerald-600" size={32} />
          <div className="flex gap-2">
            <CardTitle className="max-w-prose">{festival.festivalName}</CardTitle>
            {festival.town && <CardDescription>{festival.town}, </CardDescription>}
            <CardDescription>{festival.country}</CardDescription>
          </div>
        </div>
        <div className="flex gap-6 self-end mx-8 items-stretch">
          <Button className="bg-emerald-700 hover:bg-emerald-600" onClick={goToApplication}>
            <Send />
            {festival.applied ? "Go to application" : "Apply to festival"}
          </Button>
          <FestivalUpdateDialog />
          <EditButton href={`/festivals/${festival.id}/edit`} />
        </div>
      </div>
      <Card className="mb-6 relative">
        <CardContent className="grid-cols-2 ">
          <div className="flex items-center gap-2 mb-6">
            <Info className="text-emerald-600" />
            <CardDescription className="text-lg font-semibold text-black">Basic info</CardDescription>
          </div>
          <DetailsView data={getBasicFestivalInfo(festival)} />
        </CardContent>
      </Card>
      <Card className="relative">
        <CardContent className="grid-cols-2">
          <div className="flex items-center gap-2 mb-6">
            <NotebookTabs className="text-emerald-600" />
            <CardDescription className="text-lg font-semibold text-black">Festival details</CardDescription>
          </div>
          <DetailsView data={getFestivalDetails(festival)} />
        </CardContent>
      </Card>
      <div className="flex self-end bottom-4 right-4 m-6">
        <BackButton href="/festivals" />
      </div>
    </div>
  );
};

export default FestivalView;
