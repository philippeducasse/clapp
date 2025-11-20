import { Festival } from "@/interfaces/entities/Festival";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import _ from "lodash";

export const getFestivalBasicInfo = (festival: Festival): SectionCellProps[] => {
  if (!festival) return [];

  return [
    { title: "Festival Name", value: festival.name },
    { title: "Country", value: festival.country },
    { title: "Town", value: festival.town },
    {
      title: "Website",
      value: festival.websiteUrl,
      type: SectionCellType.Link,
    },
    { title: "Festival type", value: _.capitalize(_.lowerCase(festival.festivalType)) },
    { title: "Approximate date", value: festival.approximateDate },
  ];
};
