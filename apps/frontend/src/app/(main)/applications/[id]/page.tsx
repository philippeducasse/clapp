import { Suspense } from "react";
import ApplicationView from "@/components/page-components/applications/components/details/ApplicationView";
import DetailsViewSkeleton from "@/components/common/skeletons/DetailsViewSkeleton";

const ApplicationDetailPage = async () => {
  return (
    <Suspense fallback={<DetailsViewSkeleton />}>
      <ApplicationView />
    </Suspense>
  );
};

export default ApplicationDetailPage;
