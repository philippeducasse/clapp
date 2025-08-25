import FestivalForm from "@/components/page-components/festivals/components/form/FestivalForm";
import React from "react";
import { Actions } from "@/interfaces/Actions";

const FestivalCreationPage = () => {
  return <FestivalForm action={Actions.CREATE} />;
};

export default FestivalCreationPage;
