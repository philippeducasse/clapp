import { ControlledFormElement, SelectOptions } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { Dossier, Performance } from "@/interfaces/entities/Performance";
import { OrganisationContact } from "@/interfaces/entities/OrganisationContact";
import { Profile, EmailTemplate } from "@/interfaces/entities/Profile";
import { ApplicationMethod } from "@/interfaces/entities/Application";
import { LANGUAGES } from "@/constants/languages";
import { getOptions } from "@/helpers/formHelper";
import { interpolateEmailTemplate } from "@/helpers/emailTemplateHelper";

export interface ApplicableEntity {
  id?: number;
  name?: string;
  contacts?: OrganisationContact[];
  applicationType?: string;
}

export const getEmailTemplateOptions = (emailTemplates: EmailTemplate[]): SelectOptions[] => {
  return [
    ...emailTemplates.map((t) => ({
      value: String(t.id),
      label: t.name,
    })),
  ];
};

export const getPerformanceOptions = (performances: Performance[]): SelectOptions[] => {
  return performances.map((p) => ({
    value: String(p.id),
    label: p.performanceTitle,
  }));
};

export const getDossierOptions = (dossiers: Dossier[]): SelectOptions[] | undefined => {
  if (!dossiers.length) return;
  return dossiers.map((d) => ({
    value: String(d.id),
    label: d.name,
  }));
};

export const getApplicationFormFields = (
  entity: ApplicableEntity | null | undefined,
  performances: Performance[],
  applicationMethod: ApplicationMethod,
  profile: Profile,
  dossiers: Dossier[],
  emailTemplates: EmailTemplate[] = [],
): ControlledFormElement[] => {
  const performanceOptions = getPerformanceOptions(performances);
  const dossierOptions = getDossierOptions(dossiers);
  const emailTemplateOptions = getEmailTemplateOptions(emailTemplates);
  const userLanguageCodes = profile?.spokenLanguages ?? ["en"];
  const userLanguages = LANGUAGES.filter((lang) => userLanguageCodes.includes(lang.code));

  const defaultEmailSubject = interpolateEmailTemplate(profile?.emailSubjectDefultText, {
    firstName: profile?.firstName,
    lastName: profile?.lastName,
    entityName: entity?.name,
    currentYear: new Date().getFullYear(),
  });

  const emailApplicationFields: ControlledFormElement[] = [
    {
      label: "Email subject",
      fieldName: "emailSubject",
      type: ControlledFormElementType.TEXT,
      defaultValue: defaultEmailSubject,
    },
    {
      label: "Recipients",
      fieldName: "recipients",
      type: ControlledFormElementType.MULTI_EMAIL,
      defaultValue: entity?.contacts?.map((c) => c.email) ?? [],
      helpText: "Enter recipients, hit enter or ',' to separate them",
    },
    {
      label: "Language",
      fieldName: "language",
      type: ControlledFormElementType.SELECT,
      options: userLanguages.map((l) => ({ value: l.code, label: l.name })),
      helpText: "Provide the language for the email generation",
      defaultValue: userLanguages[0]?.code ?? "en",
    },
    {
      label: "Email Template",
      fieldName: "emailTemplate",
      type: ControlledFormElementType.SELECT,
      options: emailTemplateOptions,
      helpText: "Select a template to auto-fill the message",
      hidden: !emailTemplateOptions.length,
    },
    {
      label: "Message",
      fieldName: "message",
      type: ControlledFormElementType.TEXT_EDITOR,
    },
    {
      label: "Message length",
      fieldName: "messageLength",
      type: ControlledFormElementType.SLIDER,
      sliderOptions: {
        min: 1,
        max: 5,
        step: 1,
        labels: ["very short", "short", "normal", "long", "very long"],
      },
      defaultValue: 3 as unknown as string,
      helpText: "Set the length if generating email",
    },
  ];

  if (dossierOptions && dossierOptions?.length > 0) {
    emailApplicationFields.push({
      label: "Dossier(s)",
      fieldName: "dossiers",
      type: ControlledFormElementType.MULTI_SELECT,
      options: dossierOptions,
      defaultValue: dossierOptions.map((option) => String(option.value)),
      helpText: "Select which dossiers to attach to this application",
    });
  }

  emailApplicationFields.push({
    label: "Additional Attachments",
    fieldName: "attachmentsSent",
    type: ControlledFormElementType.FILE,
  });

  const displayedFields: ControlledFormElement[] = [
    {
      label: "Method",
      fieldName: "applicationMethod",
      type: ControlledFormElementType.SELECT,
      options: getOptions(ApplicationMethod),
      defaultValue: entity?.applicationType || "EMAIL",
      helpText:
        applicationMethod === ApplicationMethod.FORM
          ? "Selecting 'Form' implies that you have filled out and sent an organisation online form yourself."
          : applicationMethod === ApplicationMethod.UNKNOWN
            ? "Please check the organisation website before you submit an application"
            : "",
    },
    {
      label: "Performance(s)",
      fieldName: "performances",
      type: ControlledFormElementType.MULTI_SELECT,
      options: performanceOptions,
      helpText: "Select with which performances you want to apply to this organisation",
    },
  ];

  if (applicationMethod == ApplicationMethod.EMAIL) {
    displayedFields.push(...emailApplicationFields);
  }

  displayedFields.push({
    label: "Comments",
    fieldName: "comments",
    type: ControlledFormElementType.TEXT,
    helpText: "These are for you and won't be included in the application",
  });

  return displayedFields;
};