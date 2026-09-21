import React from "react";
import ResidencyBasicInfoForm from "@/components/page-components/residencies/components/form/ResidencyBasicInfoForm";
import { Action } from "@/interfaces/Enums";

const EditResidencyPage = () => {
  return <ResidencyBasicInfoForm action={Action.EDIT} />;
};

export default EditResidencyPage;
