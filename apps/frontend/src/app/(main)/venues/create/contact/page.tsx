import VenueContactsForm from "@/components/page-components/venues/components/form/VenueContactsForm";
import React from "react";
import { Action } from "@/interfaces/Enums";

const VenueCreationPage = () => {
  return <VenueContactsForm action={Action.CREATE} />;
};

export default VenueCreationPage;
