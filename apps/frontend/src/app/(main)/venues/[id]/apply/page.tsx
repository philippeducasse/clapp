import React, { Suspense } from "react";
import ApplicationForm from "@/components/page-components/applications/components/form/ManualApplicationForm";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const VenueApplicationPage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <ApplicationForm action={Action.CREATE} />
    </Suspense>
  );
};

export default VenueApplicationPage;
