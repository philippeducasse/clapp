import React from "react";
import VenueBasicInfoForm from "@/components/page-components/venues/components/form/VenueBasicInfoForm";
import { Action } from "@/interfaces/Enums";

const EditVenuePage = () => {
  return <VenueBasicInfoForm action={Action.EDIT} />;
};

export default EditVenuePage;
