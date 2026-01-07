import { Venue } from "@/interfaces/entities/Venue";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
export const getVenueDetails = (venue: Venue): SectionCellProps[] => {
  if (!venue) return [];

  return [
    { title: "Description", value: venue.description },
    { title: "Contacted?", value: venue.contacted, type: SectionCellType.Bool },
  ];
};

export const getVenueComments = (venue: Venue): SectionCellProps[] => {
  if (!venue) return [];

  return [{ title: "", value: venue?.comments }];
};
