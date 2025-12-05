import FestivalForm from "@/components/page-components/festivals/components/form/FestivalBasicInfoForm";
import React, { Suspense } from "react";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const FestivalCreationPage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <FestivalForm action={Action.CREATE} />
    </Suspense>
  );
};

export default FestivalCreationPage;
