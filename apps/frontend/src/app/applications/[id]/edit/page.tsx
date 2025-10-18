import React from "react";
import EditApplicationForm from "@/components/page-components/applications/components/form/EditApplicationForm";
import { Action } from "@/interfaces/Enums";

const EditApplicationPage = () => {
  return <EditApplicationForm action={Action.EDIT} />;
};

export default EditApplicationPage;
