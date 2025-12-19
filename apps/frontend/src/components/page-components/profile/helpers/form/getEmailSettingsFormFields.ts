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
      type: ControlledFormElementType.SELECT,
      options: getOptions(EmailHost),
      helpText: "Select the email hosting provider",
    },
    {
      label: "Email provider",
      fieldName: "otherEmailHost",
      type: ControlledFormElementType.SMTP,
      helpText:
        "The SMTP server address for sending emails (e.g., smtp.gmail.com or mail.yourprovider.com). Check your email provider's documentation if unsure.",
      register: isOtherEmailHost,
      hidden: !isOtherEmailHost,
      required: isOtherEmailHost,
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
    {
      label: "Email uses TLS?",
      fieldName: "emailUseTls",
      type: ControlledFormElementType.BOOLEAN,
      helpText: "Enable TLS/SSL encryption for secure email transmission. Recommended for most providers.",
    },
  ];

  return fields;
};
