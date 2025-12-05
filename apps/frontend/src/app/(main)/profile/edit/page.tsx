import React, { Suspense } from "react";
import ProfileForm from "@/components/page-components/profile/components/form/ProfileForm";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";

const EditProfilePage = () => {
  return (
    <Suspense fallback={<FormSkeleton />}>
      <ProfileForm action={Action.EDIT} />
    </Suspense>
  );
};

export default EditProfilePage;
