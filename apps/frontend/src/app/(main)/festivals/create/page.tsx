import FestivalForm from "@/components/page-components/festivals/components/form/FestivalBasicInfoForm";
import React from "react";
import { Action } from "@/interfaces/Enums";

const FestivalCreationPage = () => {
  return <FestivalForm action={Action.CREATE} />;
};

export default FestivalCreationPage;
