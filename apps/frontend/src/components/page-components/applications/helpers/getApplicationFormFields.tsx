import { ControlledFormElement, SelectOptions } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { Performance } from "@/interfaces/entities/Performance";
import { Festival } from "@/interfaces/entities/Festival";
import { Profile } from "@/interfaces/entities/Profile";

export const getApplicationFormFields = (
  festival: Festival,
  performances: Performance[],
  profile: Profile
): ControlledFormElement[] => {
  const performanceOptions: SelectOptions[] = performances.map((p) => ({
    value: String(p.id),
    label: p.performanceTitle,
  }));

  return [
    {
      label: "Email subject",
      fieldName: "emailSubject",
      type: ControlledFormElementType.TEXT,
      defaultValue: `${profile.firstName} ${profile.lastName} at ${festival.name} 2026`,
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
