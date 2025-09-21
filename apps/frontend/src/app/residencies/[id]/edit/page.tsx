import React from "react";
import ResidencyForm from "@/components/page-components/residencies/components/form/ResidencyForm";
import { Action } from "@/interfaces/Enums";
const EditResidencyPage = () => {
  return <ResidencyForm action={Action.EDIT} />;
};

export default EditResidencyPage;
