import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { getOptions } from "@/helpers/formHelper";
import { VenueType } from "@/interfaces/entities/Venue";

export const getVenueFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Venue ID",
      fieldName: "id",
      type: ControlledFormElementType.NUMBER,
      hidden: true,
    },
    {
      label: "Venue Name",
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
      label: "Venue Type",
      fieldName: "venueType",
      type: ControlledFormElementType.SELECT,
      options: getOptions(VenueType),
    },
    {
      label: "Contacted",
      fieldName: "contacted",
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
