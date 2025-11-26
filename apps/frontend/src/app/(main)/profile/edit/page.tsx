import React from "react";
import ProfileForm from "@/components/page-components/profile/components/form/ProfileForm";
import { Action } from "@/interfaces/Enums";

const EditProfilePage = () => {
  return <ProfileForm action={Action.EDIT} />;
};

export default EditProfilePage;
