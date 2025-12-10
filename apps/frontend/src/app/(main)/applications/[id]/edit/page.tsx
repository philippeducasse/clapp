import React from "react";
import ManualApplicationForm from "@/components/page-components/applications/components/form/ManualApplicationForm";
import { Action } from "@/interfaces/Enums";

const ManualApplicationPage = () => {
  return <ManualApplicationForm action={Action.EDIT} />;
};

export default ManualApplicationPage;
