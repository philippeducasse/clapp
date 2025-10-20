"use client";

import React, { useEffect } from "react";
import { Flag } from "lucide-react";
import { FestivalUpdateDialog } from "../update/FestivalUpdateDialog";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import {
  selectFestival,
  setSelectedFestival,
} from "@/redux/slices/festivalSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { useDispatch } from "react-redux";
import { getFestivalBasicInfo } from "../../helpers/getBasicFestivalInfo";
import { getFestivalDetails } from "../../helpers/getFestivalDetails";
import { useRouter } from "next/navigation";
import { Info, NotebookTabs } from "lucide-react";
import { refreshFestival } from "../../helpers/refreshFestival";
import { Skeleton } from "@/components/ui/skeleton";
import SendButton from "@/components/common/buttons/GenericButton";
import DetailsViewHeader from "@/components/common/details-view/DetailsViewHeader";
import DetailsViewSection from "@/components/common/details-view/DetailsViewSection";
import DetailsViewWrapper from "@/components/common/details-view/DetailsViewWrapper";
import ContactsViewSection from "@/components/common/details-view/ContactsSection";
import AddSection from "@/components/common/buttons/AddSection";
import { festivalApiService } from "@/api/festivalApiService";
import { updateFestival } from "@/redux/slices/festivalSlice";
import { toast } from "sonner";

const FestivalView = () => {
  const params = useParams();
  const dispatch = useDispatch();
  const festivalId = Number(params.id);
  const festival = useSelector((state: RootState) =>
    selectFestival(state, festivalId)
  );
  const router = useRouter();

  useEffect(() => {
    if (!festival) {
      refreshFestival(festivalId, dispatch);
    } else {
      dispatch(setSelectedFestival(festival));
    }
  }, [festivalId, festival, dispatch]);

  if (!festival) {
    return <Skeleton />;
  }

  const goToApplyPage = async () => {
    router.push(`${festivalId}/apply`);
  };

  const onConfirmDeleteContact = async (index?: number) => {
    if (!festival) return;

    try {
      // Remove contact at the given index
      const updatedContacts =
        festival.contacts?.filter((_, i) => i !== index) ?? [];

      const updatedFestival = {
        ...festival,
        contacts: updatedContacts,
      };

      await festivalApiService.updateFestival(updatedFestival);
      dispatch(updateFestival(updatedFestival));
      toast.success("Contact deleted successfully");
    } catch (error) {
      console.error("Error deleting contact:", error);
      toast.error("Failed to delete contact");
    }
  };

  return (
    <DetailsViewWrapper href="/festivals">
      <DetailsViewHeader
        title={festival.name}
        subtitle={`${festival.town && `${festival.town}`}, ${festival.country}`}
        icon={
          <Flag className="text-emerald-600 dark:text-emerald-400" size={32} />
        }
        actionElements={
          <>
            <SendButton
              onClick={goToApplyPage}
              label={
                festival.applied ? "Go to application" : "Apply to festival"
              }
              isLoading={false}
            />
            <FestivalUpdateDialog />
            <EditButton href={`/festivals/${festival.id}/edit`} />
          </>
        }
      />
      <DetailsViewSection
        title="Basic information"
        icon={<Info className="text-emerald-600 dark:text-emerald-400" />}
        data={getFestivalBasicInfo(festival)}
      />
      <DetailsViewSection
        title="Festival details"
        icon={
          <NotebookTabs className="text-emerald-600 dark:text-emerald-400" />
        }
        data={getFestivalDetails(festival)}
      />
      {festival.contacts && (
        <ContactsViewSection
          title="Contacts"
          contacts={festival.contacts}
          entityId={festivalId}
          onDelete={onConfirmDeleteContact}
        />
      )}
      <AddSection label="contact" />
    </DetailsViewWrapper>
  );
};

export default FestivalView;
