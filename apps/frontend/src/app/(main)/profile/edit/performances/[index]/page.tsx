import PerformanceForm from "@/components/page-components/performances/components/PerformanceForm";
import React from "react";
import { Action } from "@/interfaces/Enums";

const PerformanceCreationPage = () => {
  return <PerformanceForm action={Action.EDIT} />;
};

export default PerformanceCreationPage;
