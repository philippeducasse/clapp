"use client";

import PerformanceForm from "@/components/page-components/performances/components/PerformanceForm";
import React from "react";
import { Action } from "@/interfaces/Enums";
import { useParams } from "next/navigation";

const PerformanceFormPage = () => {
  const params = useParams();
  const { performanceId } = params;
  return <PerformanceForm action={performanceId === "new" ? Action.CREATE : Action.EDIT} />;
};

export default PerformanceFormPage;
