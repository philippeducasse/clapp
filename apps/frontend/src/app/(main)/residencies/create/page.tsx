import React, { Suspense } from "react";
import ResidencyForm from "@/components/page-components/residencies/components/form/ResidencyForm";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const CreateResidencyPage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <ResidencyForm action={Action.CREATE} />
    </Suspense>
  );
};

export default CreateResidencyPage;
