import { ControlledFormElement } from "@/interfaces/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";
import { getOptions } from "@/helpers/formHelper";
import { ApplicationType, FestivalType } from "@/interfaces/Festival";
export const getFestivalFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Festival Name",
      fieldName: "festivalName",
      type: ControlledFormElementType.TEXT,
      required: true,
      className: "col-span-1",
    },
    {
      label: "Website",
      fieldName: "websiteUrl",
      type: ControlledFormElementType.URL,
      className: "col-span-1",
    },
    {
      label: "Approximate Date",
      fieldName: "approximateDate",
      type: ControlledFormElementType.TEXT,
      className: "col-span-1",
      helpText: "Approximate date the festival will take place",
    },
    {
      label: "Country",
      fieldName: "country",
      type: ControlledFormElementType.TEXT,
      className: "col-span-1",
    },
    {
      label: "Town",
      fieldName: "town",
      type: ControlledFormElementType.TEXT,
      className: "col-span-1",
    },
    {
      label: "Festival Type",
      fieldName: "festivalType",
      type: ControlledFormElementType.SELECT,
      options: getOptions(FestivalType),
      className: "col-span-1",
    },
    {
      label: "Description",
      fieldName: "description",
      type: ControlledFormElementType.TEXT,
      className: "col-span-1",
    },
    {
      label: "Contact Email",
      fieldName: "contactEmail",
      type: ControlledFormElementType.EMAIL,
      className: "col-span-1",
      helpText: "Email of main person of contact",
    },
    {
      label: "Contact Person",
      fieldName: "contactPerson",
      type: ControlledFormElementType.TEXT,
      className: "col-span-1",
      helpText: "Name of main person of contact",
    },
    {
      label: "Start Date",
      fieldName: "startDate",
      type: ControlledFormElementType.DATE,
      className: "col-span-1",
      helpText: "Exact date the festival will start",
    },
    {
      label: "End Date",
      fieldName: "endDate",
      type: ControlledFormElementType.DATE,
      className: "col-span-1",
      helpText: "Exact date the festival will end",
    },
    {
      label: "Application start",
      fieldName: "applicationStart",
      type: ControlledFormElementType.TEXT,
      className: "col-span-1",
      helpText: "Approximate or exact date of when festival begins accepting applications",
    },
    {
      label: "Application end",
      fieldName: "applicationEnd",
      type: ControlledFormElementType.TEXT,
      className: "col-span-1",
    },
    {
      label: "Application type",
      fieldName: "applicationType",
      type: ControlledFormElementType.SELECT,
      options: getOptions(ApplicationType),
      className: "col-span-1",
      helpText: "How the festival accepts applications",
    },
    {
      label: "Applied",
      fieldName: "applied",
      type: ControlledFormElementType.BOOLEAN,
      className: "col-span-1",
    },
  ];
};
