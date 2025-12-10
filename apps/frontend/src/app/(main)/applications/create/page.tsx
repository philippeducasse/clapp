import React from "react";
import ManualApplicationForm from "@/components/page-components/applications/components/form/ManualApplicationForm";
import { Action } from "@/interfaces/Enums";

const CreateApplicationPage = () => {
  return <ManualApplicationForm action={Action.CREATE} />;
};

export default CreateApplicationPage;
