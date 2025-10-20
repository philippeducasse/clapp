import React from "react";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import DetailsView from "./DetailsView";
import { OrganisationContact } from "@/interfaces/entities/OrganisationContact";
import { getFestivalContacts } from "@/components/page-components/festivals/helpers/getFestivaContacts";
import { Contact2 } from "lucide-react";
import EditButton from "../buttons/EditButton";
import DeleteButton from "../buttons/DeleteButton";
import { DeleteModal } from "../modals/DeleteModal";
import { useState } from "react";

interface ContactsViewSectionProps {
  title: string;
  contacts: OrganisationContact[];
  entityId: number;
  onDelete: (index?: number) => void;
}

const ContactsViewSection = ({
  title,
  contacts,
  entityId,
  onDelete,
}: ContactsViewSectionProps) => {
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [deleteIndex, setDeleteIndex] = useState<number | undefined>();

  const handleDeleteClick = (index: number) => {
    setDeleteIndex(index);
    setOpenDeleteDialog(true);
  };

  const handleConfirmDelete = () => {
    onDelete(deleteIndex);
  };

  return (
    <>
      <DeleteModal
        open={openDeleteDialog}
        onOpenChange={setOpenDeleteDialog}
        title="Are you sure you want to delete this contact?"
        description="This cannot be undone"
        onConfirm={handleConfirmDelete}
      />
      <Card className="mb-6 relative">
        <CardContent>
          <div className="flex items-center gap-2 mb-6">
            <Contact2 className="text-emerald-600 dark:text-emerald-400" />
            <CardTitle className="text-lg font-semibold text-black dark:text-foreground">
              {title}
            </CardTitle>
          </div>
          <div className="">
            {contacts.map((contact: OrganisationContact, idx) => (
              <div key={`${contact.email}_${idx}`} className="flex flex-col">
                <DetailsView data={getFestivalContacts(contact)} />
                <div className="flex my-6 self-end mr-6 gap-2">
                  <EditButton
                    href={`${entityId}/edit/contacts/${idx}`}
                    className=""
                  />
                  <DeleteButton
                    variant="outline"
                    onDelete={() => handleDeleteClick(idx)}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </>
  );
};

export default ContactsViewSection;
