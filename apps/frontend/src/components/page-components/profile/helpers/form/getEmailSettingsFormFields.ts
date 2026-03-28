import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { EmailHost, EMAIL_HOST_CONFIG } from "@/interfaces/Enums";
import { getOptions } from "@/helpers/formHelper";
import { capitalizeFirst } from "@/utils/stringUtils";
import { EMAIL_PLACEHOLDER_HELP_TEXT } from "@/constants/emailPlaceholders";
export const getEmailPasswordHelpText = (emailHost: EmailHost | null | undefined): string => {
  if (!emailHost || emailHost === EmailHost.OTHER) {
    return EMAIL_HOST_CONFIG[EmailHost.OTHER].helpText;
  }
  const config = EMAIL_HOST_CONFIG[emailHost];
  const baseText = config.helpText;
  const docLink = config.documentationUrl
    ? ` <a href="${config.documentationUrl}" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">Detailed instructions</a>`
    : "";
  return baseText + docLink;
};

export const getEmailPortHelpText = (emailHost: EmailHost | null | undefined): string => {
  if (!emailHost || emailHost === EmailHost.OTHER) {
    return "Provide the port from which your provider receives emails. For most modern providers, this is 587.";
  }
  const config = EMAIL_HOST_CONFIG[emailHost];
  return `For ${capitalizeFirst(emailHost)}, use port ${
    config.smtpPort
  }. This is the recommended port for secure email transmission.`;
};

export const getEmailTlsHelpText = (emailHost: EmailHost | null | undefined): string => {
  if (!emailHost || emailHost === EmailHost.OTHER) {
    return "Enable TLS/SSL encryption for secure email transmission. Recommended for most providers.";
  }
  const config = EMAIL_HOST_CONFIG[emailHost];
  return config.useTls
    ? `${capitalizeFirst(
        emailHost,
      )} requires TLS/SSL encryption. This setting should be enabled for secure email transmission.`
    : `${capitalizeFirst(
        emailHost,
      )} does not require TLS encryption for this configuration. TLS can be disabled, but it is recommended you leave it .`;
};

export const getEmailSettingsFormFields = (
  isOtherEmailHost: boolean,
  selectedEmailHost?: EmailHost | null,
): ControlledFormElement[] => {
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
      helpText: getEmailPortHelpText(selectedEmailHost),
    },
    {
      label: "Email password",
      fieldName: "emailHostPassword",
      type: ControlledFormElementType.PASSWORD,
      helpText: getEmailPasswordHelpText(selectedEmailHost),
    },
    {
      label: "Email uses TLS?",
      fieldName: "emailUseTls",
      type: ControlledFormElementType.BOOLEAN,
      helpText: getEmailTlsHelpText(selectedEmailHost),
    },
    {
      label: "Default Email Subject Template",
      fieldName: "emailSubjectDefultText",
      type: ControlledFormElementType.TEXT,
      helpText: `Set a default template for email subjects. ${EMAIL_PLACEHOLDER_HELP_TEXT} For example: "{{companyName}} at {{organisation}} {{currentYear}}"`,
    },
  ];

  return fields;
};
