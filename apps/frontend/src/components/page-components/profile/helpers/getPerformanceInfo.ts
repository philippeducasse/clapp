import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { Performance } from "@/interfaces/entities/Performance";
import { capitalizeFirst } from "@/utils/stringUtils";
export const getPerformanceInfo = (performance: Performance): SectionCellProps[] => {
  if (!performance) return [];

  return [
    { title: "Title", value: performance.performanceTitle },
    { title: "Type", value: capitalizeFirst(performance.performanceType) },
    {
      title: "Genres",
      value: Array.isArray(performance.genres)
        ? performance.genres.map((genre) => capitalizeFirst(genre)).join(", ")
        : "",
    },
    { title: "Length", value: performance.length },
    { title: "Short Description", value: performance.shortDescription, type: SectionCellType.HTML },
    { title: "Long Description", value: performance.longDescription, type: SectionCellType.HTML },
    { title: "Email prompt", value: performance.emailPrompt, type: SectionCellType.HTML },
    { title: "Creation Date", value: performance.creationDate?.toString() },
  ];
};
