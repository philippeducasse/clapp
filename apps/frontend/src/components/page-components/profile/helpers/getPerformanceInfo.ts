import { SectionCellProps } from "@/interfaces/DetailsView";
import { Performance } from "@/interfaces/entities/Performance";

export const getPerformanceInfo = (
  performance: Performance
): SectionCellProps[] => {
  if (!performance) return [];

  return [
    { title: "Title", value: performance.performanceTitle },
    { title: "Type", value: performance.performanceType },
    { title: "Genres", value: performance.genres?.join(", ") },
    { title: "Length", value: performance.length },
    { title: "Short Description", value: performance.shortDescription },
    { title: "Creation Date", value: performance.creationDate?.toString() },
  ];
};
