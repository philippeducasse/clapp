import React from "react";
import ResidencyContactsForm from "@/components/page-components/residencies/components/form/ResidencyContactsForm";
import { Action } from "@/interfaces/Enums";

const EditResidencyPage = () => {
  return <ResidencyContactsForm action={Action.EDIT} />;
};

export default EditResidencyPage;
