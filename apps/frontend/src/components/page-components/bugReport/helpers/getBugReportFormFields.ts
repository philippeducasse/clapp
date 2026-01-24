import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getBugReportFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Description of the issue",
      fieldName: "message",
      type: ControlledFormElementType.TEXT_EDITOR,
      required: true,
      helpText:
        "Please provide a detailed description of the bug. Include steps to reproduce if possible.",
    },
    {
      label: "Attachments",
      fieldName: "attachments",
      type: ControlledFormElementType.FILE,
      required: false,
      helpText: "You can attach screenshots, logs, or other files to help us understand the issue.",
    },
  ];
};
