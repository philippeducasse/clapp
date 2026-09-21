import VenueBasicInfoForm from "@/components/page-components/venues/components/form/VenueBasicInfoForm";
import React from "react";
import { Action } from "@/interfaces/Enums";

const VenueCreationPage = () => {
  return <VenueBasicInfoForm action={Action.CREATE} />;
};

export default VenueCreationPage;
