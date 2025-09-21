import VenueForm from "@/components/page-components/venues/components/form/VenueForm";
import React from "react";
import { Action } from "@/interfaces/Enums";

const VenueCreationPage = () => {
  return <VenueForm action={Action.CREATE} />;
};

export default VenueCreationPage;
