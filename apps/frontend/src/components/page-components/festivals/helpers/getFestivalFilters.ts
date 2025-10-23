import { getOptions } from "@/helpers/formHelper";
import { TagAction } from "@/interfaces/Enums";
import { FilterConfig } from "@/interfaces/table/FilterCongig";

export const getFestivalFilters = (): FilterConfig[] => {
  return [
    {
      column: "country",
      label: "Countries",
      type: "select",
      options: getOptions(TagAction),
      multiple: true,
    },
    {
      column: "tag",
      label: "Tag",
      type: "select",
      options: getOptions(TagAction),
      multiple: true,
    },
  ];
};
