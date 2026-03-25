"use client";

import { EmailTemplate, Profile } from "@/interfaces/entities/Profile";
import { getEmailTemplateInfo } from "../helpers/getEmailTemplateInfo";
import { Mail } from "lucide-react";
import AuxilliarySection from "@/components/common/details-view/AuxilliarySection";

interface EmailTemplatesSectionProps {
  emailTemplates: EmailTemplate[];
  onDelete: (id: number) => void;
}

const EmailTemplatesSection = ({ emailTemplates, onDelete }: EmailTemplatesSectionProps) => {
  return (
    <>
      {emailTemplates.map((template, index) => (
        <AuxilliarySection
          key={`${template.id}_${index}`}
          title={template.name}
          icon={<Mail className="text-primary" />}
          item={template}
          index={template.id}
          entityId={"profile"}
          formatData={getEmailTemplateInfo}
          getItemKey={(template, idx) => `${template.id}_${idx}`}
          editPath="email-templates"
          onDelete={onDelete}
        />
      ))}
    </>
  );
};

export default EmailTemplatesSection;
