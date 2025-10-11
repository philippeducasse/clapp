"use client";

import React, { useEffect } from "react";
import { Flag } from "lucide-react";
import { VenueUpdateDialog } from "../update/VenueUpdateDialog";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { selectVenue, setSelectedVenue } from "@/redux/slices/venueSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { useDispatch } from "react-redux";
import { getVenueBasicInfo } from "../../helpers/getBasicVenueInfo";
import { getVenueDetails } from "../../helpers/getVenueDetails";
import { useRouter } from "next/navigation";
import { Info, NotebookTabs } from "lucide-react";
import { refreshVenue } from "../../helpers/refreshVenue";
import { Skeleton } from "@/components/ui/skeleton";
import SendButton from "@/components/common/buttons/GenericButton";
import DetailsViewHeader from "@/components/common/details-view/DetailsViewHeader";
import DetailsViewSection from "@/components/common/details-view/DetailsViewSection";
import DetailsViewWrapper from "@/components/common/details-view/DetailsViewWrapper";

const VenueView = () => {
  const params = useParams();
  const dispatch = useDispatch();
  const venueId = Number(params.id);
  const venue = useSelector((state: RootState) => selectVenue(state, venueId));
  const router = useRouter();

  useEffect(() => {
    if (!venue) {
      refreshVenue(venueId, dispatch);
    } else {
      dispatch(setSelectedVenue(venue));
    }
  }, [venueId, venue, dispatch]);

  if (!venue) {
    return <Skeleton />;
  }

  const goToApplyPage = async () => {
    router.push(`${venueId}/apply`);
  };

  return (
    <DetailsViewWrapper href="/venues">
      <DetailsViewHeader
        title={venue.name}
        subtitle={`${venue.town && `${venue.town}`}, ${venue.country}`}
        icon={<Flag className="text-emerald-600 dark:text-emerald-400" size={32} />}
        actionElements={
          <>
            <SendButton
              onClick={goToApplyPage}
              label={venue.applied ? "Go to application" : "Apply to venue"}
              isLoading={false}
            />
            <VenueUpdateDialog />
            <EditButton href={`/venues/${venue.id}/edit`} />
          </>
        }
      />
      <DetailsViewSection
        title="Basic information"
        icon={<Info className="text-emerald-600 dark:text-emerald-400" />}
        data={getVenueBasicInfo(venue)}
      />
      <DetailsViewSection
        title="Venue details"
        icon={<NotebookTabs className="text-emerald-600 dark:text-emerald-400" />}
        data={getVenueDetails(venue)}
      />
    </DetailsViewWrapper>
  );
};

export default VenueView;
