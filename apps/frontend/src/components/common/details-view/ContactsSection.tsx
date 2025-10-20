import React from "react";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import DetailsView from "./DetailsView";
import { OrganisationContact } from "@/interfaces/entities/OrganisationContact";
import { getFestivalContacts } from "@/components/page-components/festivals/helpers/getFestivaContacts";
import { Contact2 } from "lucide-react";

interface ContactsViewSectionProps {
  title: string;
  contacts: OrganisationContact[];
}

const ContactsViewSection = ({ title, contacts }: ContactsViewSectionProps) => {
  return (
    <Card className="mb-6 relative">
      <CardContent className="grid-cols-2 ">
        <div className="flex items-center gap-2 mb-6">
          <Contact2 className="text-emerald-600 dark:text-emerald-400" />
          <CardTitle className="text-lg font-semibold text-black dark:text-foreground">
            {title}
          </CardTitle>
        </div>
        <div className="col-span-2">
          {contacts.map((contact: OrganisationContact, idx) => (
            <DetailsView
              data={getFestivalContacts(contact)}
              key={`${contact.email}_idx`}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default ContactsViewSection;
