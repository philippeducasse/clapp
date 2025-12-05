import React, { Suspense } from "react";
import FestivalForm from "@/components/page-components/festivals/components/form/FestivalBasicInfoForm";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const EditFestivalPage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <FestivalForm action={Action.EDIT} />
    </Suspense>
  );
};

export default EditFestivalPage;
