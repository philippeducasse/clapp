import FestivalContactsForm from "@/components/page-components/festivals/components/form/FestivalContactsForm";
import React, { Suspense } from "react";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const FestivalCreationPage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <FestivalContactsForm action={Action.CREATE} />
    </Suspense>
  );
};

export default FestivalCreationPage;
