import { getOptions } from "@/helpers/formHelper";
import { FilterConfig } from "@/interfaces/table/FilterCongig";
import { FilterType } from "@/interfaces/forms/ControlledFormElementType";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { OrganisationType } from "@/interfaces/Enums";

export const getApplicationFilters = (): FilterConfig[] => {
  return [
    {
      column: "applicationStatus",
      label: "Status",
      type: FilterType.MULTI_SELECT,
      options: getOptions(ApplicationStatus),
      multiple: true,
    },
    {
      column: "organisationType",
      label: "Organisation Type",
      type: FilterType.MULTI_SELECT,
      options: getOptions(OrganisationType),
      multiple: true,
    },
    {
      column: "createdAt",
      label: "Application date",
      type: FilterType.DATE,
    },
  ];
};
