import { ControlledFormElement, SelectOptions } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { Performance } from "@/interfaces/entities/Performance";
import { Festival } from "@/interfaces/entities/Festival";
import { Profile } from "@/interfaces/entities/Profile";
import { ApplicationMethod } from "@/interfaces/entities/Application";
import { capitalize } from "lodash";
export const getPerformanceOptions = (performances: Performance[]): SelectOptions[] => {
  return performances.map((p) => ({
    value: String(p.id),
    label: p.performanceTitle,
  }));
};

export const getApplicationFormFields = (
  festival: Festival,
  performances: Performance[],
  profile: Profile,
  applicationMethod: ApplicationMethod.EMAIL | ApplicationMethod.FORM
): ControlledFormElement[] => {
  const performanceOptions = getPerformanceOptions(performances);
  const userLanguages = ["FRENCH", "ITALIAN", "GERMAN", "ENGLISH", "SPANISH"];

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
      defaultValue: festival?.contacts?.map((c) => c.email),
      helpText: "Enter recipients, hit enter or ',' to separate them",
    },
    {
      label: "Language",
      fieldName: "language",
      type: ControlledFormElementType.SELECT,
      options: userLanguages.map((l) => ({ value: l, label: capitalize(l) })),
      helpText: "Provide the language for the email generation",
      defaultValue: "ENGLISH",
    },
    {
      label: "Message",
      fieldName: "message",
      type: ControlledFormElementType.TEXT_EDITOR,
    },
    {
      label: "Attachments",
      fieldName: "attachmentsSent",
      type: ControlledFormElementType.FILE,
    },
  ];

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
    helpText: "These are for you and won't be included in the application"
  });

  return displayedFields;
};
