import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
export const getUploadFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Excel file",
      fieldName: "excel",
      type: ControlledFormElementType.EXCEL,
      required: true,
    },
  ];
};
