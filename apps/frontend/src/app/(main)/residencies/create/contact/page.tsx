import ResidencyContactsForm from "@/components/page-components/residencies/components/form/ResidencyContactsForm";
import React from "react";
import { Action } from "@/interfaces/Enums";

const ResidencyCreationPage = () => {
  return <ResidencyContactsForm action={Action.CREATE} />;
};

export default ResidencyCreationPage;
