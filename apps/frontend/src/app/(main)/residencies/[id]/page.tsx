import { Suspense } from "react";
import ResidencyView from "@/components/page-components/residencies/components/details/ResidencyView";
import DetailsViewSkeleton from "@/components/common/skeletons/DetailsViewSkeleton";

const ResidencyDetailsPage = () => {
  return (
    <Suspense fallback={<DetailsViewSkeleton />}>
      <ResidencyView />
    </Suspense>
  );
};

export default ResidencyDetailsPage;
