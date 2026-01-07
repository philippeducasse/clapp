import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getResidencyFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Residency ID",
      fieldName: "id",
      type: ControlledFormElementType.NUMBER,
      hidden: true,
    },
    {
      label: "Residency Name",
      fieldName: "name",
      type: ControlledFormElementType.TEXT,
      required: true,
    },
    {
      label: "Website",
      fieldName: "websiteUrl",
      type: ControlledFormElementType.URL,
    },
    {
      label: "Approximate Date",
      fieldName: "approximateDate",
      type: ControlledFormElementType.TEXT,
      helpText: "Approximate date the residency will take place",
    },
    {
      label: "Country",
      fieldName: "country",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Town",
      fieldName: "town",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Start Date",
      fieldName: "startDate",
      type: ControlledFormElementType.DATE,
      helpText: "Exact date the residency will start",
    },
    {
      label: "End Date",
      fieldName: "endDate",
      type: ControlledFormElementType.DATE,
      helpText: "Exact date the residency will end",
    },
    {
      label: "Application start",
      fieldName: "applicationStart",
      type: ControlledFormElementType.TEXT,
      helpText: "Approximate or exact date of when residency begins accepting applications",
    },
    {
      label: "Application end",
      fieldName: "applicationEnd",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Applied",
      fieldName: "applied",
      type: ControlledFormElementType.BOOLEAN,
    },
    {
      label: "Comments",
      fieldName: "comments",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Description",
      fieldName: "description",
      type: ControlledFormElementType.TEXT_AREA,
    },
  ];
};
