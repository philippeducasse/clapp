import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getForgotPasswordFormFields = (): ControlledFormElement[] => [
  {
    label: "email",
    fieldName: "email",
    type: ControlledFormElementType.EMAIL,
    required: true,
    helpText:
      "Please enter the email for your account. If a user is found with the associated email address, an email will be send to the inbox with a reset link",
  },
];
