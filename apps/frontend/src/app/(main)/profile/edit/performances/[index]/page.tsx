import PerformanceForm from "@/components/page-components/performances/components/PerformanceForm";
import React, { Suspense } from "react";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const PerformanceCreationPage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <PerformanceForm action={Action.EDIT} />
    </Suspense>
  );
};

export default PerformanceCreationPage;
