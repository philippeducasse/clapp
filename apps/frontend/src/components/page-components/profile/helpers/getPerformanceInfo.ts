import { SectionCellProps } from "@/interfaces/DetailsView";
import { Performance } from "@/interfaces/entities/Performance";
import { capitalizeFirst } from "@/utils/stringUtils";
export const getPerformanceInfo = (performance: Performance): SectionCellProps[] => {
  if (!performance) return [];

  return [
    { title: "Title", value: performance.performanceTitle },
    { title: "Type", value: capitalizeFirst(performance.performanceType) },
    {
      title: "Genres",
      value: performance.genres?.map((genre) => capitalizeFirst(genre)).join(", "),
    },
    { title: "Length", value: performance.length },
    { title: "Short Description", value: performance.shortDescription },
    { title: "Creation Date", value: performance.creationDate?.toString() },
  ];
};
