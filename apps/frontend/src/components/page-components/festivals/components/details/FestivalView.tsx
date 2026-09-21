"use client";

import React, { useEffect, useState } from "react";
import { Flag, Send } from "lucide-react";
import { FestivalUpdateDialog } from "../update/FestivalUpdateDialog";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { selectFestival } from "@/redux/slices/festivalSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { useDispatch } from "react-redux";
import { getFestivalBasicInfo } from "../../helpers/getBasicFestivalInfo";
import { getFestivalDetails } from "../../helpers/getFestivalDetails";
import { useRouter } from "next/navigation";
import { Info, NotebookTabs } from "lucide-react";
import { refreshFestival } from "../../helpers/refreshFestival";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import DetailsViewHeader from "@/components/common/details-view/DetailsViewHeader";
import DetailsViewSection from "@/components/common/details-view/DetailsViewSection";
import DetailsViewWrapper from "@/components/common/details-view/DetailsViewWrapper";
import ContactsViewSection from "@/components/common/details-view/ContactsSection";
import RemindersCard from "@/components/common/details-view/RemindersCard";
import CommentsCard from "@/components/common/details-view/CommentsCard";
import AddSection from "@/components/common/buttons/AddSection";
import { festivalApiService } from "@/api/festivalApiService";
import { updateFestival } from "@/redux/slices/festivalSlice";
import { OrganisationType } from "@/interfaces/Enums";
import DeleteButton from "@/components/common/buttons/DeleteButton";
import { DeleteModal } from "@/components/common/modals/DeleteModal";

const FestivalView = () => {
  const params = useParams();
  const dispatch = useDispatch();
  const festivalId = Number(params.id);
  const festival = useSelector((state: RootState) => selectFestival(state, festivalId));
  const router = useRouter();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [itemName, setItemName] = useState<"festival" | "contact">("festival");
  const [deleteIndex, setDeleteIndex] = useState<number | undefined>();

  useEffect(() => {
    if (!festival) {
      refreshFestival(festivalId, dispatch);
    }
  }, [festivalId, festival, dispatch]);

  if (!festival) {
    return <Skeleton />;
  }

  const goToApplyPage = async () => {
    router.push(`${festivalId}/apply`);
  };

  const handleDelete = (entity: "festival" | "contact", index?: number) => {
    setDeleteIndex(index);
    setItemName(entity);
    setOpenDeleteDialog(true);
  };

  const onConfirmDelete = async () => {
    if (!festival) return;

    try {
      if (itemName === "festival") {
        await festivalApiService.remove(festivalId);
        router.push("/festivals");
      } else if (itemName === "contact" && deleteIndex !== undefined) {
        const updatedContacts = festival.contacts?.filter((_, i) => i !== deleteIndex) ?? [];

        const updatedFestival = {
          ...festival,
          contacts: updatedContacts,
        };
        await festivalApiService.update(updatedFestival);
        dispatch(updateFestival(updatedFestival));
      }
    } catch (error) {
      console.error(`Error deleting ${itemName}:`, error);
    }
  };

  return (
    <DetailsViewWrapper href="/festivals">
      <DeleteModal
        open={openDeleteDialog}
        onOpenChange={setOpenDeleteDialog}
        onConfirm={onConfirmDelete}
        itemName={itemName}
      />
      <DetailsViewHeader
        title={festival.name}
        subtitle={`${festival.town && `${festival.town}`}, ${festival.country}`}
        icon={<Flag className="text-primary" size={32} />}
        entityId={festival.id}
        tagApiMethod={festivalApiService.tag}
        updateSlice={updateFestival}
        actionElements={
          <>
            <Button onClick={goToApplyPage}>
              <Send /> Apply
            </Button>
            <FestivalUpdateDialog />
            <EditButton href={`/festivals/${festival.id}/edit`} />
            <DeleteButton
              onDelete={() => handleDelete("festival", festivalId)}
            />
          </>
        }
      />
      <div className="flex gap-6">
        <div className="flex-1">
          <DetailsViewSection
            title="Basic information"
            icon={<Info className="text-primary" />}
            data={getFestivalBasicInfo(festival)}
            ribbonType="tag"
            ribbonValue={festival.tag}
          />
        </div>
        <div className="w-80 space-y-6">
          <CommentsCard
            comments={festival.comments || ""}
            onSave={async (comments) => {
              const updatedFestival = { ...festival, comments };
              await festivalApiService.update(updatedFestival);
              dispatch(updateFestival(updatedFestival));
            }}
          />
          <RemindersCard organisationType={OrganisationType.FESTIVAL} entityId={festivalId} />
        </div>
      </div>
      <DetailsViewSection
        title="Festival details"
        icon={<NotebookTabs className="text-primary" />}
        data={getFestivalDetails(festival)}
      />
      {festival.contacts && festival.contacts.length > 0 && (
        <ContactsViewSection
          title="Contacts"
          contacts={festival.contacts}
          entityId={festivalId}
          onDelete={(index) => handleDelete("contact", index)}
        />
      )}
      <AddSection
        label="contact"
        href={`${festivalId}/edit/contacts/${festival.contacts?.length ?? 0}`}
      />
    </DetailsViewWrapper>
  );
};

export default FestivalView;
