import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { EmailHost } from "@/interfaces/Enums";
import { getOptions } from "@/helpers/formHelper";

export const getEmailSettingsFormFields = (isOtherEmailHost: boolean): ControlledFormElement[] => {
  const fields: ControlledFormElement[] = [
    {
      label: "Email",
      fieldName: "emailHostUser",
      type: ControlledFormElementType.EMAIL,
      helpText:
        "Enter the email address you want applications to be sent from. This can differ from the email you use to log in to this app",
    },
    {
      label: "Email provider",
      fieldName: "emailHost",
      type: isOtherEmailHost ? ControlledFormElementType.TEXT : ControlledFormElementType.SELECT,
      options: getOptions(EmailHost),
      helpText: "Select the email hosting provider",
      register: isOtherEmailHost,
    },

    {
      label: "Email port",
      fieldName: "emailPort",
      type: ControlledFormElementType.NUMBER,
      helpText:
        "Provide the port from which your provider receives emails. For most modern providers, this is 587.",
    },
    {
      label: "Email password",
      fieldName: "emailHostPassword",
      type: ControlledFormElementType.PASSWORD,
      helpText: "Enter the password for your email account",
    },
  ];

  return fields;
};
