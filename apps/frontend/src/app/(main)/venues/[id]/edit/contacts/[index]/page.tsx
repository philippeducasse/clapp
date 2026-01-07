import React from "react";
import VenueContactsForm from "@/components/page-components/venues/components/form/VenueContactsForm";
import { Action } from "@/interfaces/Enums";

const EditVenuePage = () => {
  return <VenueContactsForm action={Action.EDIT} />;
};

export default EditVenuePage;
