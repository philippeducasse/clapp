import React, { Suspense } from "react";
import FestivalContactsForm from "@/components/page-components/festivals/components/form/FestivalContactsForm";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const EditFestivalPage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <FestivalContactsForm action={Action.EDIT} />
    </Suspense>
  );
};

export default EditFestivalPage;
