import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getPreferencesFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Date Format",
      fieldName: "dateFormat",
      type: ControlledFormElementType.SELECT,
      required: false,
      options: [
        { value: "DD/MM/YYYY", label: "DD/MM/YYYY" },
        { value: "MM/DD/YYYY", label: "MM/DD/YYYY" },
        { value: "YYYY-MM-DD", label: "YYYY-MM-DD" },
      ],
      helpText: "Choose your preferred date format for the application",
    },
    {
      label: "Table Size",
      fieldName: "tableSize",
      type: ControlledFormElementType.SELECT,
      required: false,
      options: [
        { value: "compact", label: "Compact (10 rows)" },
        { value: "medium", label: "Medium (25 rows)" },
        { value: "large", label: "Large (50 rows)" },
      ],
      helpText: "Choose how many rows to display in tables by default",
    },
  ];
};