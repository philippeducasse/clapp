import { getOptions } from "@/helpers/formHelper";
import { TagAction } from "@/interfaces/Enums";
import { FilterConfig } from "@/interfaces/table/FilterCongig";
import { FilterType } from "@/interfaces/forms/ControlledFormElementType";
import { VenueType } from "@/interfaces/entities/Venue";

export const getVenueFilters = (): FilterConfig[] => {
  return [
    {
      column: "tag",
      label: "Tags",
      type: FilterType.MULTI_SELECT,
      options: getOptions(TagAction),
      multiple: true,
    },
    {
      column: "venueType",
      label: "Type",
      type: FilterType.MULTI_SELECT,
      options: getOptions(VenueType),
      multiple: true,
    },
    {
      column: "country",
      label: "Country",
      type: FilterType.MULTI_SELECT,
      options: [
        { label: "France", value: "france" },
        { label: "Germany", value: "germany" },
        { label: "Italy", value: "italy" },
        { label: "Poland", value: "poland" },
        { label: "Netherlands", value: "netherlands" },
        { label: "Switzerland", value: "switzerland" },
        { label: "Austria", value: "austria" },
        { label: "Denmark", value: "denmark" },
        { label: "Belgium", value: "belgium" },
        { label: "Spain", value: "spain" },
        { label: "Portugal", value: "portugal" },
      ],
      multiple: true,
    },
    {
      column: "contacted",
      label: "Contacted?",
      type: FilterType.SELECT,
      options: [
        { value: "CONTACTED", label: "Contacted" },
        { value: "NOT_CONTACTED", label: "Not contacted" },
      ],
    },
  ];
};
