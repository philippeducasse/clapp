import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
export const getRegistrationFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Email",
      fieldName: "email",
      type: ControlledFormElementType.EMAIL,
    },
    {
      label: "Password",
      fieldName: "password",
      type: ControlledFormElementType.PASSWORD,
    },
    {
      label: "Password (confirm)",
      fieldName: "passwordConfirm",
      type: ControlledFormElementType.PASSWORD,
    },
  ];
};
