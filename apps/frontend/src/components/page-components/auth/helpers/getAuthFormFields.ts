import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
export const getAuthFormFields = (isRegistration: boolean = false): ControlledFormElement[] => {
  const fields = [
    {
      label: "Email",
      fieldName: "email",
      type: ControlledFormElementType.EMAIL,
      required: true,
    },
    {
      label: "Password",
      fieldName: "password",
      type: ControlledFormElementType.PASSWORD,
      required: true,
    },
  ];
  if (isRegistration) {
    fields.push({
      label: "Password (confirm)",
      fieldName: "passwordConfirm",
      type: ControlledFormElementType.PASSWORD,
      required: true,
    });
  }
  return fields;
};
