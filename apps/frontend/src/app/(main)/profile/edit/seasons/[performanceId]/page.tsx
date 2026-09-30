"use client";

import ApplicationSeasonForm from "@/components/page-components/applications/components/ApplicationSeasonForm";
import { Action } from "@/interfaces/Enums";
import { useParams } from "next/navigation";

const ApplicationSeasonFormPage = () => {
  const params = useParams();
  const { performanceId } = params;
  return <ApplicationSeasonForm action={performanceId === "new" ? Action.CREATE : Action.EDIT} />;
};

export default ApplicationSeasonFormPage;
