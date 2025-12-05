import VenueForm from "@/components/page-components/venues/components/form/VenueForm";
import React, { Suspense } from "react";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const VenueCreationPage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <VenueForm action={Action.CREATE} />
    </Suspense>
  );
};

export default VenueCreationPage;
