import { Residency } from "@/interfaces/Residency";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";

export const getResidencyBasicInfo = (residency: Residency): SectionCellProps[] => {
  if (!residency) return [];

  return [
    { title: "Name", value: residency.name },
    { title: "Location", value: residency.location },
    { title: "Website", value: residency.website, type: SectionCellType.Link },
    { title: "Start Date", value: residency.startDate },
    { title: "End Date", value: residency.endDate },
  ];
};
