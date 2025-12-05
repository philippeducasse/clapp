import React, { Suspense } from "react";
import VenueForm from "@/components/page-components/venues/components/form/VenueForm";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const EditVenuePage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <VenueForm action={Action.EDIT} />
    </Suspense>
  );
};

export default EditVenuePage;
