import { Residency } from "@/interfaces/Residency";
import { SectionCellProps } from "@/interfaces/DetailsView";

export const getResidencyDetails = (residency: Residency): SectionCellProps[] => {
  if (!residency) return [];

  return [
    { title: "Description", value: residency.description },
    { title: "Status", value: residency.status },
    { title: "Last Updated", value: residency.lastUpdated },
  ];
};
