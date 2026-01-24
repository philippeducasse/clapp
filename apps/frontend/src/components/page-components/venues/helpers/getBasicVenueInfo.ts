import { Venue } from "@/interfaces/entities/Venue";
import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { capitalizeFirst } from "@/utils/stringUtils";

export const getVenueBasicInfo = (venue: Venue): SectionCellProps[] => {
  if (!venue) return [];

  return [
    { title: "Venue Name", value: venue.name },
    { title: "Country", value: venue.country },
    { title: "Town", value: venue.town },
    {
      title: "Website",
      value: venue.websiteUrl,
      type: SectionCellType.Link,
    },
    { title: "Venue type", value: capitalizeFirst(venue.venueType) },
    { title: "Approximate date", value: venue.approximateDate },
  ];
};
