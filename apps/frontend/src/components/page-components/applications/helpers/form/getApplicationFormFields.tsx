import { ControlledFormElement, SelectOptions } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { Dossier, Performance } from "@/interfaces/entities/Performance";
import { Festival } from "@/interfaces/entities/Festival";
import { Profile } from "@/interfaces/entities/Profile";
import { ApplicationMethod } from "@/interfaces/entities/Application";
import { LANGUAGES } from "@/constants/languages";

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
  festival: Festival,
  performances: Performance[],
  applicationMethod: ApplicationMethod.EMAIL | ApplicationMethod.FORM,
  profile: Profile,
  dossiers: Dossier[]
): ControlledFormElement[] => {
  const performanceOptions = getPerformanceOptions(performances);
  const dossierOptions = getDossierOptions(dossiers);

  const userLanguageCodes = profile?.spokenLanguages ?? ["en"];
  const userLanguages = LANGUAGES.filter((lang) => userLanguageCodes.includes(lang.code));

  const emailApplicationFields: ControlledFormElement[] = [
    {
      label: "Email subject",
      fieldName: "emailSubject",
      type: ControlledFormElementType.TEXT,
      defaultValue:
        festival?.name &&
        `${profile?.firstName ?? "Philippe"} ${profile?.lastName ?? "Ducasse"} at ${
          festival?.name
        } 2026`,
    },
    {
      label: "Recipients",
      fieldName: "recipients",
      type: ControlledFormElementType.MULTI_EMAIL,
      defaultValue: festival?.contacts?.map((c) => c.email) ?? [],
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
      options: [
        { value: "EMAIL", label: "Email" },
        { value: "FORM", label: "Form" },
      ],
      defaultValue: festival?.applicationType ?? "EMAIL",
      helpText:
        applicationMethod == ApplicationMethod.FORM
          ? "Selecting 'Form' implies that you have filled out and sent an organisation online form yourself."
          : "",
    },
    {
      label: "Performance(s)",
      fieldName: "performances",
      type: ControlledFormElementType.MULTI_SELECT,
      options: performanceOptions,
      helpText: "Select with which performances you want to apply to this festival",
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
