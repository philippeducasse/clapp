import { Venue } from "@/interfaces/entities/Venue";
import { SectionCellProps } from "@/interfaces/DetailsView";

export const getVenueContacts = (venue: Venue): SectionCellProps[] => {
  if (!venue?.contacts || venue.contacts.length === 0) {
    return [];
  }

  return venue.contacts.map((contact) => ({
    title: contact.name || "Contact",
    value: contact.email || contact.phone || "No contact info",
  }));
};
