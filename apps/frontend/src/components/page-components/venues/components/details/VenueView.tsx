"use client";

import React, { useEffect, useState } from "react";
import { Flag, Send } from "lucide-react";
import { VenueUpdateDialog } from "../update/VenueUpdateDialog";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { selectVenue, updateVenue } from "@/redux/slices/venueSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { useDispatch } from "react-redux";
import { getVenueBasicInfo } from "../../helpers/getBasicVenueInfo";
import { getVenueDetails } from "../../helpers/getVenueDetails";
import { useRouter } from "next/navigation";
import { Info, NotebookTabs } from "lucide-react";
import { refreshVenue } from "../../helpers/refreshVenue";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import DetailsViewHeader from "@/components/common/details-view/DetailsViewHeader";
import DetailsViewSection from "@/components/common/details-view/DetailsViewSection";
import DetailsViewWrapper from "@/components/common/details-view/DetailsViewWrapper";
import ContactsViewSection from "@/components/common/details-view/ContactsSection";
import AddSection from "@/components/common/buttons/AddSection";
import { venueApiService } from "@/api/venueApiService";
import DeleteButton from "@/components/common/buttons/DeleteButton";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import RemindersCard from "@/components/common/details-view/RemindersCard";
import CommentsCard from "@/components/common/details-view/CommentsCard";
import { OrganisationType } from "@/interfaces/Enums";

const VenueView = () => {
  const params = useParams();
  const dispatch = useDispatch();
  const venueId = Number(params.id);
  const venue = useSelector((state: RootState) => selectVenue(state, venueId));
  const router = useRouter();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [itemName, setItemName] = useState<"venue" | "contact">("venue");
  const [deleteIndex, setDeleteIndex] = useState<number | undefined>();

  useEffect(() => {
    if (!venue) {
      refreshVenue(venueId, dispatch);
    }
  }, [venueId, venue, dispatch]);

  if (!venue) {
    return <Skeleton />;
  }

  const goToApplyPage = async () => {
    router.push(`${venueId}/apply`);
  };

  const handleDelete = (entity: "venue" | "contact", index?: number) => {
    setDeleteIndex(index);
    setItemName(entity);
    setOpenDeleteDialog(true);
  };

  const onConfirmDelete = async () => {
    if (!venue) return;

    try {
      if (itemName === "venue") {
        await venueApiService.remove(venueId);
        router.push("/venues");
      } else if (itemName === "contact" && deleteIndex !== undefined) {
        const updatedContacts = venue.contacts?.filter((_, i) => i !== deleteIndex) ?? [];

        const updatedVenue = {
          ...venue,
          contacts: updatedContacts,
        };
        await venueApiService.update(updatedVenue);
        dispatch(updateVenue(updatedVenue));
      }
    } catch (error) {
      console.error(`Error deleting ${itemName}:`, error);
    }
  };

  return (
    <DetailsViewWrapper href="/venues">
      <DeleteModal
        open={openDeleteDialog}
        onOpenChange={setOpenDeleteDialog}
        onConfirm={onConfirmDelete}
        itemName={itemName}
      />
      <DetailsViewHeader
        title={venue.name}
        subtitle={`${venue.town && `${venue.town}`}, ${venue.country}`}
        icon={<Flag className="text-primary" size={32} />}
        entityId={venue.id}
        tagApiMethod={venueApiService.tag}
        updateSlice={updateVenue}
        actionElements={
          <>
            <Button onClick={goToApplyPage}>
              <Send /> Apply
            </Button>
            <VenueUpdateDialog />
            <EditButton href={`/venues/${venue.id}/edit`} />
            <DeleteButton
              onDelete={() => handleDelete("venue", venueId)}
            />
          </>
        }
      />
      <div className="flex gap-6">
        <div className="flex-1">
          <DetailsViewSection
            title="Basic information"
            icon={<Info className="text-primary" />}
            data={getVenueBasicInfo(venue)}
            ribbonType="tag"
            ribbonValue={venue.tag}
          />
        </div>
        <div className="w-80 space-y-6">
          <CommentsCard
            comments={venue.comments || ""}
            onSave={async (comments) => {
              const updatedVenue = { ...venue, comments };
              await venueApiService.update(updatedVenue);
              dispatch(updateVenue(updatedVenue));
            }}
          />
          <RemindersCard organisationType={OrganisationType.VENUE} entityId={venueId} />
        </div>
      </div>
      <DetailsViewSection
        title="Venue details"
        icon={<NotebookTabs className="text-primary" />}
        data={getVenueDetails(venue)}
      />
      {venue.contacts && venue.contacts.length > 0 && (
        <ContactsViewSection
          title="Contacts"
          contacts={venue.contacts}
          entityId={venueId}
          onDelete={(index) => handleDelete("contact", index)}
        />
      )}
      <AddSection
        label="contact"
        href={`${venueId}/edit/contacts/${venue.contacts?.length ?? 0}`}
      />
    </DetailsViewWrapper>
  );
};

export default VenueView;
