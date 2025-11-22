import { Application } from "@/interfaces/entities/Application";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import _ from "lodash";
import { capitalizeFirst } from "@/utils/stringUtils";

export const getApplicationBasicInfo = (application: Application): SectionCellProps[] => {
  if (!application) return [];
  return [
    {
      title: "Organisation Name",
      value: application.organisation.name,
      type: SectionCellType.Link,
      linkTo: `/${application.organisationType.toLowerCase()}s/${application.organisation.id}`,
      target: "_self",
    },
    {
      title: "Status",
      value: capitalizeFirst(application.applicationStatus),
    },
    {
      title: "Email recipients",
      value: application.emailRecipients?.join(", "),
    },
    {
      title: "Email subject",
      value: application.emailSubject,
    },
    {
      title: "Email content",
      value: application.message,
      type: SectionCellType.HTML,
    },
    {
      title: "Comments",
      value: application.comments as string,
    },
    {
      title: "Application type",
      value: _.capitalize(application.applicationMethod as string),
    },
  ];
};
