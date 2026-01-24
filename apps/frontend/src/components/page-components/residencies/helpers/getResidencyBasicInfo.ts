import { Residency } from "@/interfaces/entities/Residency";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";

export const getResidencyBasicInfo = (
  residency: Residency
): SectionCellProps[] => {
  if (!residency) return [];

  return [
    { title: "Name", value: residency.name },
    { title: "Country", value: residency.country },
    { title: "Town", value: residency.town },
    { title: "Location", value: residency.location },
    { title: "Website", value: residency.website, type: SectionCellType.Link },
    { title: "Approximate date", value: residency.approximateDate },
    { title: "Start Date", value: residency.startDate },
    { title: "End Date", value: residency.endDate },
  ];
};
