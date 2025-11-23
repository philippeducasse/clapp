import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { getOptions } from "@/helpers/formHelper";
import { PerformanceType, PerformanceGenre } from "@/interfaces/entities/Performance";

export const getPerformanceFormFields = (): ControlledFormElement[] => {
  return [
    {
      label: "Performance ID",
      fieldName: "id",
      type: ControlledFormElementType.NUMBER,
      hidden: true,
    },
    {
      label: "Performance Title",
      fieldName: "performanceTitle",
      type: ControlledFormElementType.TEXT,
      required: true,
    },
    {
      label: "Short Description",
      fieldName: "shortDescription",
      type: ControlledFormElementType.TEXT_AREA,
      helpText: "A brief description of your performance",
    },
    {
      label: "Trailer",
      fieldName: "trailer",
      type: ControlledFormElementType.URL,
      helpText: "Link to a trailer or video of your performance",
    },
    {
      label: "Length",
      fieldName: "length",
      type: ControlledFormElementType.TEXT,
      helpText: "Duration of the performance (e.g., 45 minutes, 1 hour)",
    },
    {
      label: "Long Description",
      fieldName: "longDescription",
      type: ControlledFormElementType.TEXT_EDITOR,
      helpText: "Detailed description of your performance",
    },
    {
      label: "Creation Date",
      fieldName: "creationDate",
      type: ControlledFormElementType.DATE,
      helpText: "When was this performance created",
    },
    {
      label: "Performance Type",
      fieldName: "performanceType",
      type: ControlledFormElementType.SELECT,
      options: getOptions(PerformanceType),
    },
    {
      label: "Genres",
      fieldName: "genres",
      type: ControlledFormElementType.MULTI_SELECT,
      options: getOptions(PerformanceGenre),
      helpText: "Select all genres that apply to your performance",
    },
  ];
};
