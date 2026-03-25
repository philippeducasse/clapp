import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getEmailTemplateFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Template ID",
      fieldName: "id",
      type: ControlledFormElementType.NUMBER,
      hidden: true,
    },
    {
      label: "Template Name",
      fieldName: "name",
      type: ControlledFormElementType.TEXT,
      required: true,
      helpText: "A name to identify this template (e.g., 'Festival Introduction', 'Short Pitch')",
    },
    {
      label: "Email Subject Template",
      fieldName: "subjectTemplate",
      type: ControlledFormElementType.TEXT,
      helpText:
        "Set the email subject for this template. Use {{firstName}}, {{lastName}}, {{entityName}}, and {{currentYear}} as placeholders that will be replaced automatically.",
    },
    {
      label: "Content",
      fieldName: "content",
      type: ControlledFormElementType.TEXT_EDITOR,
      required: true,
      helpText: "Write your email template content",
    },
  ];
};
