import { Residency } from "@/interfaces/entities/Residency";
import { SectionCellProps } from "@/interfaces/DetailsView";

export const getResidencyContacts = (residency: Residency): SectionCellProps[] => {
  if (!residency?.contacts || residency.contacts.length === 0) {
    return [];
  }

  return residency.contacts.map((contact) => ({
    title: contact.name || "Contact",
    value: contact.email || contact.phone || "No contact info",
  }));
};
