import { ControlledFormElement, SelectOptions } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { Performance } from "@/interfaces/entities/Performance";
import { Festival } from "@/interfaces/entities/Festival";
import { Profile } from "@/interfaces/entities/Profile";
import { ApplicationMethod } from "@/interfaces/entities/Application";
export const getPerformanceOptions = (performances: Performance[]): SelectOptions[] => {
  return performances.map((p) => ({
    value: String(p.id),
    label: p.performanceTitle,
  }));
};

export const getApplicationFormFields = (
  festival: Festival,
  performances: Performance[],
  profile: Profile
): ControlledFormElement[] => {
  const performanceOptions = getPerformanceOptions(performances);

  return [
    {
      label: "Method",
      fieldName: "applicationMethod",
      type: ControlledFormElementType.SELECT,
      options: [
        { value: "EMAIL", label: "Email" },
        { value: "FORM", label: "Form" },
      ],
      defaultValue: ApplicationMethod.EMAIL,
    },
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
      type: ControlledFormElementType.TEXT,
      defaultValue: festival?.contacts?.[0]?.email ?? "",
      helpText: "Please separate emails by a comma",
    },
    {
      label: "Performance(s)",
      fieldName: "performances",
      type: ControlledFormElementType.MULTI_SELECT,
      options: performanceOptions,
      helpText: "Select with which performances you want to apply to this festival",
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
};
