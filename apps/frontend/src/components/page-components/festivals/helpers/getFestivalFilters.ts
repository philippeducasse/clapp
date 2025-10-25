import {getOptions} from "@/helpers/formHelper";
import {TagAction} from "@/interfaces/Enums";
import {FilterConfig} from "@/interfaces/table/FilterCongig";
import {FilterType} from "@/interfaces/forms/ControlledFormElementType";

export const getFestivalFilters = (): FilterConfig[] => {
  return [
    {
      column: "tag",
      label: "Tags",
      type: FilterType.MULTI_SELECT,
      options: getOptions(TagAction),
      multiple: true,
    },
    {
      column: "country",
      label: "Country",
      type: FilterType.MULTI_SELECT,
      options: [{label: "France", value:"france"}, {label: "Germany", value:"germany"}],
      multiple: true,
    },
  ];
};
