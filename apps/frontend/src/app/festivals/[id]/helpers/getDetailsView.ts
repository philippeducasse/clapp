import { Festival } from "@/interfaces/Festival";
import { SectionCellProps } from "@/interfaces/DetailsView";

export const getDetailsView = (festival: Festival): SectionCellProps[] => {
  if (!festival) return [];

  return [
    { title: "Festival Name", value: festival.festivalName },
    { title: "Country", value: festival.country },
  ];
};
