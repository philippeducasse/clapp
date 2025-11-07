import { Application } from "@/interfaces/entities/Application";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import _ from "lodash";

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
      value: _.capitalize(_.lowerCase(application.applicationStatus)),
    },
    {
      title: "Email Subject",
      value: application.emailSubject,
    },
    {
      title: "Email content",
      value: application.message,
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
