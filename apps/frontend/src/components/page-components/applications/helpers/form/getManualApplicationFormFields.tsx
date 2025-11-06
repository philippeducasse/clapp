import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { Performance } from "@/interfaces/entities/Performance";
import { ApplicationStatusOptions } from "@/interfaces/forms/StatusOptions";
import { getPerformanceOptions } from "./getApplicationFormFields";
import { getOptions } from "@/helpers/formHelper";
import { ApplicationMethod } from "@/interfaces/entities/Application";
import { OrganisationType } from "@/interfaces/Enums";
export const getManualApplicationFormFields = (
  performances: Performance[]
): ControlledFormElement[] => {
  const performanceOptions = getPerformanceOptions(performances);
  return [
    {
      label: "Organisation type",
      fieldName: "organisationType",
      type: ControlledFormElementType.SELECT,
      options: getOptions(OrganisationType),
    },
    {
      label: "Organisation",
      fieldName: "organisationId",
      type: ControlledFormElementType.SEARCH,
    },
    {
      label: "Method",
      fieldName: "applicationMethod",
      type: ControlledFormElementType.SELECT,
      helpText: "How did you apply to this festival?",
      options: getOptions(ApplicationMethod),
    },
    {
      label: "Status",
      fieldName: "applicationStatus",
      type: ControlledFormElementType.SELECT,
      options: ApplicationStatusOptions,
      required: true,
    },
    {
      label: "Comments",
      fieldName: "comments",
      type: ControlledFormElementType.TEXT_EDITOR,
    },
    {
      label: "Performance(s)",
      fieldName: "performanceIds",
      type: ControlledFormElementType.MULTI_SELECT,
      options: performanceOptions,
      helpText: "Select with which performances you want to apply to this festival",
    },
  ];
};
