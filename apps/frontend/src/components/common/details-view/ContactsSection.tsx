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
    <>
      {contacts.map((contact, index) => (
        <AuxilliarySection
          key={`${contact.email}_${index}`}
          title={title}
          icon={<Contact2 className="text-primary" />}
          item={contact}
          index={index}
          entityId={entityId}
          formatData={getFestivalContacts}
          getItemKey={(contact, idx) => `${contact.email}_${idx}`}
          editPath="contacts"
          onDelete={onDelete}
        />
      ))}
    </>
  );
};

export default ContactsViewSection;
