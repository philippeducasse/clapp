import React from "react";
import ApplicationForm from "@/components/page-components/applications/components/form/ApplicationForm";
import { EntityName } from "@/interfaces/Enums";

const VenueApplicationPage = () => {
  return <ApplicationForm entityName={EntityName.VENUE} />;
};

export default VenueApplicationPage;
