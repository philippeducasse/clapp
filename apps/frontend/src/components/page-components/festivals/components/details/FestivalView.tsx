"use client";

import React, { useEffect } from "react";
import { Flag } from "lucide-react";
import { FestivalUpdateDialog } from "../update/FestivalUpdateDialog";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { selectFestival, setSelectedFestival } from "@/redux/slices/festivalSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { useDispatch } from "react-redux";
import { getFestivalBasicInfo } from "../../helpers/getBasicFestivalInfo";
import { getFestivalDetails } from "../../helpers/getFestivalDetails";
import { useRouter } from "next/navigation";
import { Info, NotebookTabs } from "lucide-react";
import { refreshFestival } from "../../helpers/refreshFestival";
import { Skeleton } from "@/components/ui/skeleton";
import SendButton from "@/components/common/buttons/GenericButton";
import DetailsViewHeader from "@/components/common/details-view/DetailsViewHeader";
import DetailsViewSection from "@/components/common/details-view/DetailsViewSection";
import DetailsViewWrapper from "@/components/common/details-view/DetailsViewWrapper";

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

  const goToApplyPage = async () => {
    router.push(`${festivalId}/apply`);
  };

  return (
    <DetailsViewWrapper href="/festivals">
      <DetailsViewHeader
        title={festival.name}
        subtitle={`${festival.town && `${festival.town}`}, ${festival.country}`}
        icon={<Flag className="text-emerald-600 dark:text-emerald-400" size={32} />}
        actionElements={
          <>
            <SendButton
              onClick={goToApplyPage}
              label={festival.applied ? "Go to application" : "Apply to festival"}
              isLoading={false}
            />
            <FestivalUpdateDialog />
            <EditButton href={`/festivals/${festival.id}/edit`} />
          </>
        }
      />
      <DetailsViewSection
        title="Basic information"
        icon={<Info className="text-emerald-600 dark:text-emerald-400" />}
        data={getFestivalBasicInfo(festival)}
      />
      <DetailsViewSection
        title="Festival details"
        icon={<NotebookTabs className="text-emerald-600 dark:text-emerald-400" />}
        data={getFestivalDetails(festival)}
      />
    </DetailsViewWrapper>
  );
};

export default FestivalView;
