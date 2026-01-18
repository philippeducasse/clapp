import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getReminderFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Message",
      fieldName: "message",
      type: ControlledFormElementType.TEXT_AREA,
    },
    {
      label: "Remind at",
      fieldName: "remindAt",
      type: ControlledFormElementType.DATE,
    },
  ];
};
