import { Festival } from "@/interfaces/Festival";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { capitalize } from "lodash";
export const getDetailsView = (festival: Festival): SectionCellProps[] => {
  if (!festival) return [];

  return [
    { title: "Festival Name", value: festival.festivalName },
    { title: "Country", value: festival.country },
    { title: "Town", value: festival.town },
    { title: "Website", value: festival.websiteUrl, type: SectionCellType.Link },
    { title: "Festival type", value: capitalize(festival.festivalType) },
    { title: "Approximate date", value: festival.approximateDate },
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
