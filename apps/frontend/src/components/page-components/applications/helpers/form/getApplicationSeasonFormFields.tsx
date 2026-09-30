import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getApplicationSeasonFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Name",
      fieldName: "name",
      type: ControlledFormElementType.TEXT,
      helpText: "Season name, e.g. '2027' or 'Christmas'",
    },
  ];
};
