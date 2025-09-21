import { Festival } from "@/interfaces/entities/Festival";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { capitalize } from "lodash";
export const getFestivalDetails = (festival: Festival): SectionCellProps[] => {
  if (!festival) return [];

  return [
    { title: "Start date", value: festival?.startDate },
    { title: "End date", value: festival?.endDate },
    { title: "Description", value: festival.description },
    { title: "Applied?", value: festival.applied, type: SectionCellType.Bool },
    { title: "Application start", value: festival.applicationStart },
    { title: "Application end", value: festival.applicationEnd },
    { title: "Application type", value: capitalize(festival.applicationType) },
    { title: "Contact person", value: festival.contactPerson },
    { title: "Contact email", value: festival.contactEmail },
  ];
};
