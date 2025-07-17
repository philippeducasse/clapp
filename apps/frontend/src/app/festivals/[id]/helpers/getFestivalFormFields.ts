import { ControlledFormElement } from "@/interfaces/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";

export const getFestivalFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Festival Name",
      fieldName: "festivalName",
      type: ControlledFormElementType.TEXT,
      required: true,
      className: "col-span-1",
    },
  ];
};
