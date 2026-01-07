"use client";

import React, { useEffect, useState } from "react";
import { University, MessageSquare, Send } from "lucide-react";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { selectResidency, updateResidency } from "@/redux/slices/residencySlice";
import { RootState } from "@/redux/store";
import { useDispatch } from "react-redux";
import { getResidencyBasicInfo } from "../../helpers/getResidencyBasicInfo";
import { getResidencyDetails, getResidencyComments } from "../../helpers/getResidencyDetails";
import { useRouter } from "next/navigation";
import { Info, NotebookTabs } from "lucide-react";
import { refreshResidency } from "../../helpers/refreshResidency";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import DetailsViewHeader from "@/components/common/details-view/DetailsViewHeader";
import DetailsViewSection from "@/components/common/details-view/DetailsViewSection";
import DetailsViewWrapper from "@/components/common/details-view/DetailsViewWrapper";
import ContactsViewSection from "@/components/common/details-view/ContactsSection";
import AddSection from "@/components/common/buttons/AddSection";
import { residencyApiService } from "@/api/residencyApiService";
import DeleteButton from "@/components/common/buttons/DeleteButton";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import { ResidencyUpdateDialog } from "../update/ResidencyUpdateDialog";
import { useParams } from "next/navigation";

const ResidencyView = () => {
  const params = useParams();
  const dispatch = useDispatch();
  const residencyId = Number(params.id);
  const residency = useSelector((state: RootState) => selectResidency(state, residencyId));
  const router = useRouter();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [itemName, setItemName] = useState<"residency" | "contact">("residency");
  const [deleteIndex, setDeleteIndex] = useState<number | undefined>();

  useEffect(() => {
    if (!residency) {
      refreshResidency(residencyId, dispatch);
    }
  }, [residencyId, residency, dispatch]);

  if (!residency) {
    return <Skeleton />;
  }

  const goToApplyPage = async () => {
    router.push(`/residencies/${residencyId}/apply`);
  };

  const handleDelete = (entity: "residency" | "contact", index?: number) => {
    setDeleteIndex(index);
    setItemName(entity);
    setOpenDeleteDialog(true);
  };

  const onConfirmDelete = async () => {
    if (!residency) return;

    try {
      if (itemName === "residency") {
        await residencyApiService.remove(residencyId);
        router.push("/residencies");
      } else if (itemName === "contact" && deleteIndex !== undefined) {
        const updatedContacts = residency.contacts?.filter((_, i) => i !== deleteIndex) ?? [];

        const updatedResidency = {
          ...residency,
          contacts: updatedContacts,
        };
        await residencyApiService.update(updatedResidency);
        dispatch(updateResidency(updatedResidency));
      }
    } catch (error) {
      console.error(`Error deleting ${itemName}:`, error);
    }
  };

  return (
    <DetailsViewWrapper href="/residencies">
      <DeleteModal
        open={openDeleteDialog}
        onOpenChange={setOpenDeleteDialog}
        onConfirm={onConfirmDelete}
        itemName={itemName}
      />
      <DetailsViewHeader
        title={residency.name}
        subtitle={`${residency.town && `${residency.town}`}, ${residency.country}`}
        icon={<University className="text-emerald-600 dark:text-emerald-400" size={32} />}
        entityId={residency.id}
        tagApiMethod={residencyApiService.tag}
        updateSlice={updateResidency}
        actionElements={
          <>
            <Button onClick={goToApplyPage}>
              <Send /> Apply
            </Button>
            <ResidencyUpdateDialog />
            <EditButton href={`/residencies/${residency.id}/edit`} />
            <DeleteButton
              variant={"outline"}
              className="text-red-500 border border-red-500 hover:text-red-400 hover:bg-background"
              onDelete={() => handleDelete("residency", residencyId)}
            />
          </>
        }
      />
      <DetailsViewSection
        title="Basic information"
        icon={<Info className="text-emerald-600 dark:text-emerald-400" />}
        data={getResidencyBasicInfo(residency)}
        ribbonType="tag"
        ribbonValue={residency.tag}
      />
      {residency.comments && (
        <DetailsViewSection
          title="Comments"
          icon={<MessageSquare className="text-emerald-600 dark:text-emerald-400" />}
          data={getResidencyComments(residency)}
        />
      )}
      <DetailsViewSection
        title="Residency details"
        icon={<NotebookTabs className="text-emerald-600 dark:text-emerald-400" />}
        data={getResidencyDetails(residency)}
      />
      {residency.contacts && residency.contacts.length > 0 && (
        <ContactsViewSection
          title="Contacts"
          contacts={residency.contacts}
          entityId={residencyId}
          onDelete={(index) => handleDelete("contact", index)}
        />
      )}
      <AddSection
        label="contact"
        href={`${residencyId}/edit/contacts/${residency.contacts?.length ?? 0}`}
      />
    </DetailsViewWrapper>
  );
};

export default ResidencyView;
