import { Suspense } from "react";
import FestivalView from "../../../../components/page-components/festivals/components/details/FestivalView";
import DetailsViewSkeleton from "@/components/common/skeletons/DetailsViewSkeleton";

const FestivalDetailPage = async () => {
  return (
    <Suspense fallback={<DetailsViewSkeleton />}>
      <FestivalView />
    </Suspense>
  );
};

export default FestivalDetailPage;
