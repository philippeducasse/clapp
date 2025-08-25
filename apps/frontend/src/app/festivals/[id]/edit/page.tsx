import React from "react";
import FestivalForm from "../../../../components/page-components/festivals/components/form/FestivalForm";
import { Actions } from "@/interfaces/Actions";
const EditFestivalPage = () => {
  return <FestivalForm action={Actions.EDIT} />;
};

export default EditFestivalPage;
