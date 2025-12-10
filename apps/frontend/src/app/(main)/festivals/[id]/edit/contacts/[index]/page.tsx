import React from "react";
import FestivalContactsForm from "@/components/page-components/festivals/components/form/FestivalContactsForm";
import { Action } from "@/interfaces/Enums";

const EditFestivalPage = () => {
  return <FestivalContactsForm action={Action.EDIT} />;
};

export default EditFestivalPage;
