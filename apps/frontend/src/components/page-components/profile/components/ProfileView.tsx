"use client";

// import React, { useEffect, useState } from "react";
import { CircleUser, PartyPopper } from "lucide-react";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
// import { useDispatch } from "react-redux";
import { getBasicProfileInfo } from "../helpers/getBasicProfileInfo";
import { getProfileContactInfo } from "../helpers/getProfileContactInfo";
// import { getProfileDetails, getProfileComments } from "../../helpers/getProfileDetails";
// import { useRouter } from "next/navigation";
import { Info, NotebookTabs } from "lucide-react";
// import { Skeleton } from "@/components/ui/skeleton";
// import { Button } from "@/components/ui/button";
import DetailsViewHeader from "@/components/common/details-view/DetailsViewHeader";
import DetailsViewSection from "@/components/common/details-view/DetailsViewSection";
import DetailsViewWrapper from "@/components/common/details-view/DetailsViewWrapper";
import AddSection from "@/components/common/buttons/AddSection";
// import { profileApiService } from "@/api/profileApiService";
import { selectProfile } from "@/redux/slices/authSlice";
// import { updateProfile } from "@/redux/slices/profileSlice";
// import DeleteButton from "@/components/common/buttons/DeleteButton";
// import { DeleteModal } from "@/components/common/modals/DeleteModal";
import PerformanceViewSection from "./PerformanceViewSection";

const ProfileView = () => {
  const params = useParams();
  // const dispatch = useDispatch();
  const profileId = Number(params.id);
  // const router = useRouter();
  const profile = useSelector((state: RootState) => selectProfile(state));

  // const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  // const [itemName, setItemName] = useState<"profile" | "contact" | "performance">("profile");
  // const [deleteIndex, setDeleteIndex] = useState<number | undefined>();

  // const handleDelete = (entity: "profile" | "contact" | "performance", index?: number) => {
  //   setDeleteIndex(index);
  //   setItemName(entity);
  //   setOpenDeleteDialog(true);
  // };
  //   const onConfirmDelete = async () => {

  //     try {
  //       if (itemName === "profile") {
  //         await profileApiService.remove(profileId);
  //         router.push("/profiles");
  //       } else if (itemName === "contact" && deleteIndex !== undefined) {
  //         // Remove contact at the given index
  //         const updatedContacts = profile.contacts?.filter((_, i) => i !== deleteIndex) ?? [];

  //         const updatedProfile = {
  //           ...profile,
  //           contacts: updatedContacts,
  //         };
  //         await profileApiService.update(updatedProfile);
  //         dispatch(updateProfile(updatedProfile));
  //       }
  //     } catch (error) {
  //       console.error(`Error deleting ${itemName}:`, error);
  //     }
  //   };
  if (!profile) return;
  return (
    <DetailsViewWrapper href="/profile">
      {/* <DeleteModal
        open={openDeleteDialog}
        onOpenChange={setOpenDeleteDialog}
        onConfirm={onConfirmDelete}
        itemName={itemName}
      /> */}
      <DetailsViewHeader
        title={profile?.artistName ?? "Profile"}
        subtitle={`${profile?.firstName}, ${profile.lastName}`}
        icon={<CircleUser className="text-emerald-600 dark:text-emerald-400" size={32} />}
        entityId={profile.id}
        actionElements={
          <>
            <EditButton href={`/profile/edit`} />
            {/* <DeleteButton
              variant={"outline"}
              className="text-red-500 border border-red-500 hover:text-red-400 hover:bg-background"
              onDelete={() => handleDelete("profile", profileId)}
            /> */}
          </>
        }
      />
      <DetailsViewSection
        title="Basic information"
        icon={<Info className="text-emerald-600 dark:text-emerald-400" />}
        data={getBasicProfileInfo(profile)}
      />

      <DetailsViewSection
        title="Contact details"
        icon={<NotebookTabs className="text-emerald-600 dark:text-emerald-400" />}
        data={getProfileContactInfo(profile)}
      />
      {profile.performances && profile.performances.length > 0 && (
        <>
          <DetailsViewHeader
            title={"Performances"}
            icon={<PartyPopper className="text-emerald-600 dark:text-emerald-400" size={32} />}
          />
          <PerformanceViewSection
            performances={profile.performances}
            entityId={profileId}
            // onDelete={(index) => handleDelete("performance", index)}
            onDelete={(index) => console.log("performance", index)}
          />
        </>
      )}
      <AddSection
        label="performance"
        href={`/profile/performances/${profile.performances?.length ?? 0}/create`}
      />
    </DetailsViewWrapper>
  );
};

export default ProfileView;
