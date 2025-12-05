import React, { Suspense } from "react";
import ApplicationForm from "@/components/page-components/applications/components/form/ApplicationForm";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const FestivalApplicationPage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <ApplicationForm />
    </Suspense>
  );
};

export default FestivalApplicationPage;
