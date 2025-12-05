import { Suspense } from "react";
import VenueView from "@/components/page-components/venues/components/details/VenueView";
import DetailsViewSkeleton from "@/components/common/skeletons/DetailsViewSkeleton";

const VenueDetailPage = async () => {
  return (
    <Suspense fallback={<DetailsViewSkeleton />}>
      <VenueView />
    </Suspense>
  );
};

export default VenueDetailPage;
