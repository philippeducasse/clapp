import React from "react";
import ApplicationForm from "@/components/page-components/applications/components/form/EditApplicationForm";
import { Action } from "@/interfaces/Enums";

const VenueApplicationPage = () => {
  return <ApplicationForm action={Action.CREATE} />;
};

export default VenueApplicationPage;
