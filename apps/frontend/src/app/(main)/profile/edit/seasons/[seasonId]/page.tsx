"use client";

import ApplicationSeasonForm from "@/components/page-components/applications/components/form/ApplicationSeasonForm";
import { Action } from "@/interfaces/Enums";
import { useParams } from "next/navigation";

const ApplicationSeasonFormPage = () => {
  const params = useParams();
  const { seasonId } = params;
  return <ApplicationSeasonForm action={seasonId === "new" ? Action.CREATE : Action.EDIT} />;
};

export default ApplicationSeasonFormPage;
