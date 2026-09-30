import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { Performance } from "@/interfaces/entities/Performance";
import { ApplicationStatusOptions } from "@/interfaces/forms/StatusOptions";
import { getPerformanceOptions, getSeasonOptions } from "./getApplicationFormFields";
import { getOptions } from "@/helpers/formHelper";
import { ApplicationMethod, ApplicationSeason } from "@/interfaces/entities/Application";
import { OrganisationType, Action } from "@/interfaces/Enums";

export const getManualApplicationFormFields = (
  performances: Performance[],
  seasons: ApplicationSeason[],
): ControlledFormElement[] => {
  const performanceOptions = getPerformanceOptions(performances);
  const seasonOptions = getSeasonOptions(seasons);
  return [
    {
      label: "Organisation type",
      fieldName: "organisationType",
      type: ControlledFormElementType.SELECT,
      options: getOptions(OrganisationType),
      action: Action.CREATE,
    },
    {
      label: "Organisation",
      fieldName: "organisation",
      type: ControlledFormElementType.SEARCH,
      action: Action.CREATE,
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
      fieldName: "status",
      type: ControlledFormElementType.SELECT,
      options: ApplicationStatusOptions,
      required: true,
    },
    {
      label: "Performance(s)",
      fieldName: "performanceIds",
      type: ControlledFormElementType.MULTI_SELECT,
      options: performanceOptions,
      helpText:
        "Select with which performances you want to apply to this festival. Dossiers will automatically be attached.",
    },
    {
      label: "Season",
      fieldName: "applicationSeason",
      type: ControlledFormElementType.SELECT,
      helpText: "Which season is this application for?",
      options: seasonOptions,
      defaultValue: seasonOptions && seasonOptions[0],
    },
    {
      label: "Comments",
      fieldName: "comments",
      type: ControlledFormElementType.TEXT_EDITOR,
    },
  ];
};
