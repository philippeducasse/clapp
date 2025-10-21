import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
// import { Performance } from "@/interfaces/entities/Performance";
import { ApplicationStatusOptions } from "@/interfaces/forms/StatusOptions";

export const getEditApplicationFormFields = (): //   performances: Performance[]
//   profile: Profile
ControlledFormElement[] => {
  //   const performanceOptions: SelectOptions[] = performances.map((p) => ({
  //     value: String(p.id),
  //     label: p.performanceTitle,
  //   }));

  return [
    {
      label: "Status",
      fieldName: "applicationStatus",
      type: ControlledFormElementType.SELECT,
      options: ApplicationStatusOptions,
    },
    {
      label: "Comments",
      fieldName: "comments",
      type: ControlledFormElementType.TEXT_EDITOR,
    },
    // {
    //   label: "Performance(s)",
    //   fieldName: "performances",
    //   type: ControlledFormElementType.MULTI_SELECT,
    //   options: performanceOptions,
    //   helpText: "Select with which performances you want to apply to this festival",
    // },
  ];
};
