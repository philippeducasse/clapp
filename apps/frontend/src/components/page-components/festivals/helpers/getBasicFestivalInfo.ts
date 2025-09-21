import { Festival } from "@/interfaces/entities/Festival";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { capitalize } from "lodash";

export const getFestivalBasicInfo = (
  festival: Festival
): SectionCellProps[] => {
  if (!festival) return [];

  return [
    { title: "Festival Name", value: festival.festivalName },
    { title: "Country", value: festival.country },
    { title: "Town", value: festival.town },
    {
      title: "Website",
      value: festival.websiteUrl,
      type: SectionCellType.Link,
    },
    { title: "Festival type", value: capitalize(festival.festivalType) },
    { title: "Approximate date", value: festival.approximateDate },
  ];
};
