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
      label: "Conntacted",
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
