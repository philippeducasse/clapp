import React from "react";
import ResidencyForm from "@/components/page-components/residencies/components/form/ResidencyForm";
import { Action } from "@/interfaces/Enums";

const CreateResidencyPage = () => {
  return <ResidencyForm action={Action.CREATE} />;
};

export default CreateResidencyPage;
