import React from "react";
import ResidencyBasicInfoForm from "@/components/page-components/residencies/components/form/ResidencyBasicInfoForm";
import { Action } from "@/interfaces/Enums";

const CreateResidencyPage = () => {
  return <ResidencyBasicInfoForm action={Action.CREATE} />;
};

export default CreateResidencyPage;
