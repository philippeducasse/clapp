import React, { Suspense } from "react";
import ManualApplicationForm from "@/components/page-components/applications/components/form/ManualApplicationForm";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const CreateApplicationPage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <ManualApplicationForm action={Action.CREATE} />
    </Suspense>
  );
};

export default CreateApplicationPage;
