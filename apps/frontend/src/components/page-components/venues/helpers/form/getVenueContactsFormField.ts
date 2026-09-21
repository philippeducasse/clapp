import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getVenueContactsFormField = (
  isEdit: boolean = false
): ControlledFormElement[] => {
  return [
    {
      label: "Email",
      fieldName: "email",
      type: ControlledFormElementType.EMAIL,
      required: isEdit,
    },
    {
      label: "Name",
      fieldName: "name",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Role",
      fieldName: "role",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Phone",
      fieldName: "phone",
      type: ControlledFormElementType.TEXT,
      helpText: "Please also include the country code",
    },
  ];
};
