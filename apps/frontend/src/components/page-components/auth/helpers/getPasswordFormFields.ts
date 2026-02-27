import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getPasswordFormFields = (): ControlledFormElement[] => [
  {
    label: "New password",
    fieldName: "newPassword",
    type: ControlledFormElementType.PASSWORD,
    required: true,
  },
  {
    label: "Password (confirm)",
    fieldName: "newPasswordConfirm",
    type: ControlledFormElementType.PASSWORD,
    required: true,
  },
];
