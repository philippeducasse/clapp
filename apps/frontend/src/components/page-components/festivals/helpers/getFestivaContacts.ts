import { SectionCellProps } from "@/interfaces/DetailsView";
import { OrganisationContact } from "@/interfaces/entities/OrganisationContact";

export const getFestivalContacts = (
  contact: OrganisationContact
): SectionCellProps[] => {
  if (!contact) return [];

  return [
    { title: "Email", value: contact?.email },
    { title: "name", value: contact?.name },
    { title: "Role", value: contact.role },
    { title: "Phone", value: contact.phone },
  ];
};
