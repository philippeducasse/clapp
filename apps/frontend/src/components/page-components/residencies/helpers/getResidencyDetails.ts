import { Residency } from "@/interfaces/entities/Residency";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { capitalizeFirst } from "@/utils/stringUtils";

export const getResidencyDetails = (residency: Residency): SectionCellProps[] => {
  if (!residency) return [];

  return [
    { title: "Description", value: residency.description },
    { title: "Applied?", value: residency.applied, type: SectionCellType.Bool },
    { title: "Application type", value: capitalizeFirst(residency.applicationType) },
    { title: "Application start", value: residency.applicationStart },
    { title: "Application end", value: residency.applicationEnd },
    { title: "Status", value: residency.status },
    { title: "Last Updated", value: residency.lastUpdated },
  ];
};

export const getResidencyComments = (residency: Residency): SectionCellProps[] => {
  if (!residency) return [];

  return [{ title: "", value: residency?.comments }];
};
