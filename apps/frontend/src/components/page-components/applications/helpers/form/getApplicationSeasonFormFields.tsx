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
    {
      label: "Set as default season",
      fieldName: "isDefault",
      type: ControlledFormElementType.BOOLEAN,
      helpText:
        "The default season is preselected on all new applications. Only one season can be the default.",
    },
  ];
};
