import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { getOptions } from "@/helpers/formHelper";
import { FestivalType, ApplicationType } from "@/interfaces/entities/Festival";
export const getFestivalFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Festival ID",
      fieldName: "id",
      type: ControlledFormElementType.NUMBER,
      hidden: true,
    },
    {
      label: "Festival Name",
      fieldName: "festivalName",
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
      helpText: "Approximate date the festival will take place",
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
      label: "Festival Type",
      fieldName: "festivalType",
      type: ControlledFormElementType.SELECT,
      options: getOptions(FestivalType),
    },
    {
      label: "Contact Email",
      fieldName: "contactEmail",
      type: ControlledFormElementType.EMAIL,
      helpText: "Email of main person of contact",
    },
    {
      label: "Contact Person",
      fieldName: "contactPerson",
      type: ControlledFormElementType.TEXT,
      helpText: "Name of main person of contact",
    },
    {
      label: "Start Date",
      fieldName: "startDate",
      type: ControlledFormElementType.DATE,
      helpText: "Exact date the festival will start",
    },
    {
      label: "End Date",
      fieldName: "endDate",
      type: ControlledFormElementType.DATE,
      helpText: "Exact date the festival will end",
    },
    {
      label: "Application start",
      fieldName: "applicationStart",
      type: ControlledFormElementType.TEXT,
      helpText:
        "Approximate or exact date of when festival begins accepting applications",
    },
    {
      label: "Application end",
      fieldName: "applicationEnd",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Application type",
      fieldName: "applicationType",
      type: ControlledFormElementType.SELECT,
      options: getOptions(ApplicationType),
      helpText: "How the festival accepts applications",
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
