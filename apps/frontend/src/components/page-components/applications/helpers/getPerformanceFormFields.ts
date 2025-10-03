import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getApplicationFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Performance",
      fieldName: "emailSubject",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Message",
      fieldName: "message",
      type: ControlledFormElementType.TEXT_EDITOR,
    },
    {
      label: "Attachments",
      fieldName: "attachmentsSent",
      type: ControlledFormElementType.FILE,
    },
  ];
};
