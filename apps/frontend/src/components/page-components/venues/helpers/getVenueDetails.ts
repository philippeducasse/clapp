import { Venue } from "@/interfaces/entities/Venue";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { capitalize } from "lodash";
export const getVenueDetails = (venue: Venue): SectionCellProps[] => {
  if (!venue) return [];

  return [
    { title: "Start date", value: venue?.startDate },
    { title: "End date", value: venue?.endDate },
    { title: "Description", value: venue.description },
    { title: "Applied?", value: venue.applied, type: SectionCellType.Bool },
    { title: "Application start", value: venue.applicationStart },
    { title: "Application end", value: venue.applicationEnd },
    { title: "Application type", value: capitalize(venue.applicationType) },
    { title: "Contact person", value: venue.contactPerson },
    { title: "Contact email", value: venue.contactEmail },
  ];
};
