import { SectionCellProps } from "@/interfaces/DetailsView";
import { ApplicationSeason } from "@/interfaces/entities/Application";
import { Profile } from "@/interfaces/entities/Profile";
import { formatDate } from "@/utils/stringUtils";

export const getApplicationSeasonsInfo = (
  applicationSeason: ApplicationSeason,
): SectionCellProps[] => {
  return [
    { title: "Season name", value: applicationSeason.name },
    { title: "Creation date", value: applicationSeason.createdAt ? formatDate(applicationSeason.createdAt) : "-" },
  ];
};
