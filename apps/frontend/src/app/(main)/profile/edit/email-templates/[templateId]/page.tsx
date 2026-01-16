"use client";

import EmailTemplateForm from "@/components/page-components/profile/components/form/EmailTemplateForm";
import React from "react";
import { Action } from "@/interfaces/Enums";
import { useParams } from "next/navigation";

const EmailTemplateFormPage = () => {
  const params = useParams();
  const { templateId } = params;
  return <EmailTemplateForm action={templateId === "new" ? Action.CREATE : Action.EDIT} />;
};

export default EmailTemplateFormPage;
