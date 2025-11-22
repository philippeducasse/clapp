import React from "react";
import { OrganisationContact } from "@/interfaces/entities/OrganisationContact";
import { getFestivalContacts } from "@/components/page-components/festivals/helpers/getFestivaContacts";
import { Contact2 } from "lucide-react";
import AuxilliarySection from "./AuxilliarySection";

interface ContactsViewSectionProps {
  title: string;
  contacts: OrganisationContact[];
  entityId: number;
  onDelete: (index: number) => void;
}

const ContactsViewSection = ({
  title,
  contacts,
  entityId,
  onDelete,
}: ContactsViewSectionProps) => {
  return (
    <AuxilliarySection
      title={title}
      icon={<Contact2 className="text-emerald-600 dark:text-emerald-400" />}
      items={contacts}
      entityId={entityId}
      formatData={getFestivalContacts}
      getItemKey={(contact, idx) => `${contact.email}_${idx}`}
      editPath="contacts"
      onDelete={onDelete}
    />
  );
};

export default ContactsViewSection;
