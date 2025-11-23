import PerformanceForm from "@/components/page-components/performances/components/PerformanceForm";
import React from "react";
import { Action } from "@/interfaces/Enums";

const PerformanceEditPage = () => {
  return <PerformanceForm action={Action.EDIT} />;
};

export default PerformanceEditPage;
