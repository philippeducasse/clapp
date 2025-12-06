"use client";

import PerformanceForm from "@/components/page-components/performances/components/PerformanceForm";
import React, { Suspense } from "react";
import { Action } from "@/interfaces/Enums";
import FormSkeleton from "@/components/common/skeletons/FormSkeleton";
import { useParams } from "next/navigation";
const PerformanceFormPage = () => {
  const params = useParams();
  const { performanceId } = params;
  return (
    <Suspense fallback={<FormSkeleton />}>
      <PerformanceForm action={performanceId === "new" ? Action.CREATE : Action.EDIT} />
    </Suspense>
  );
};

export default PerformanceFormPage;
