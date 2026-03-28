import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { EMAIL_PLACEHOLDER_HELP_TEXT } from "@/constants/emailPlaceholders";

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
      label: "Email Subject",
      fieldName: "subject",
      type: ControlledFormElementType.TEXT,
      helpText: `Set the email subject for this template. ${EMAIL_PLACEHOLDER_HELP_TEXT}`,
    },
    {
      label: "Content",
      fieldName: "content",
      type: ControlledFormElementType.TEXT_EDITOR,
      required: true,
    },
  ];
};
