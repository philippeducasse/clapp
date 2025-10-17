import { Application } from "@/interfaces/entities/Application";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { capitalize } from "lodash";
import { StatusBadge } from "@/components/common/StatusBadge";

export const getApplicationBasicInfo = (
  application: Application
): SectionCellProps[] => {
  if (!application) return [];

  return [
    {
      title: "Organisation Name",
      value: application.organisation.name,
      type: SectionCellType.Link,
      linkTo: `application.organisation.id`,
    },
    {
      title: "Status",
      value: capitalize(application.applicationStatus),
      //   element: <StatusBadge capitalize(application.applicationStatus) />,
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
      title: "Application type",
      value: capitalize(application.applicationMethod as string),
    },
  ];
};
