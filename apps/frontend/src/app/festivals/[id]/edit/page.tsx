import React from "react";
import FestivalForm from "@/components/page-components/festivals/components/form/FestivalForm";
import { Action } from "@/interfaces/Enums";
const EditFestivalPage = () => {
  return <FestivalForm action={Action.EDIT} />;
};

export default EditFestivalPage;
