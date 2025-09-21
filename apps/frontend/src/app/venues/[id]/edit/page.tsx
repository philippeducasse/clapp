import React from "react";
import VenueForm from "@/components/page-components/venues/components/form/FestivalForm";
import { Action } from "@/interfaces/Enums";
const EditVenuePage = () => {
  return <VenueForm action={Action.EDIT} />;
};

export default EditVenuePage;
