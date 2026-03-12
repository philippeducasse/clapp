"use client";

import React, { useState } from "react";
import { CircleUser, Cog } from "lucide-react";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { RootState } from "@/redux/store";
import { useDispatch } from "react-redux";
import { getBasicProfileInfo } from "../helpers/getBasicProfileInfo";
import { getProfileContactInfo } from "../helpers/getProfileContactInfo";
import { useRouter } from "next/navigation";
import { Info, NotebookTabs } from "lucide-react";
import DetailsViewHeader from "@/components/common/details-view/DetailsViewHeader";
import DetailsViewSection from "@/components/common/details-view/DetailsViewSection";
import DetailsViewWrapper from "@/components/common/details-view/DetailsViewWrapper";
import AddSection from "@/components/common/buttons/AddSection";
import { profileApiService } from "@/api/profileApiService";
import { performanceApiService } from "@/api/performanceApiService";
import { selectProfile, updateProfile } from "@/redux/slices/authSlice";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import PerformanceViewSection from "./PerformanceViewSection";
import EmailTemplatesSection from "./EmailTemplatesSection";
import OAuthEmailSection from "./OAuthEmailSection";
import { Profile } from "@/interfaces/entities/Profile";
import { Performance } from "@/interfaces/entities/Performance";
import DetailsTabs, { Tab } from "@/components/common/details-view/DetailsTabs";
import { getPreferencesInfo } from "../helpers/getPreferencesInfo";
import { useHashTab } from "@/hooks/useHashTab";
import Link from "next/link";
import ProfileRemindersCard from "./ProfileRemindersCard";
import DeleteButton from "@/components/common/buttons/DeleteButton";
import { Button } from "@/components/ui/button";

const ProfileView = () => {
  const dispatch = useDispatch();
  const router = useRouter();
  const profile = useSelector((state: RootState) => selectProfile(state));

  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [itemName, setItemName] = useState<"profile" | "performance" | "email template">(
    "performance",
  );
  const [idToDelete, setIdToDelete] = useState<number | undefined>();
  const { activeTab, handleTabChange } = useHashTab("basic-information");

  const handleDelete = (entity: "profile" | "performance" | "email template", index?: number) => {
    setIdToDelete(index);
    setItemName(entity);
    setOpenDeleteDialog(true);
  };
  const onConfirmDelete = async () => {
    try {
      if (itemName === "profile" && profile) {
        await profileApiService.remove(profile.id);
        router.push("/profiles");
      } else if (itemName === "performance" && idToDelete !== undefined && profile) {
        await performanceApiService.remove(idToDelete);

        const updatedperformances =
          profile.performances?.filter((p: Performance) => p.id !== idToDelete) ?? [];
        const updatedProfile: Profile = {
          ...profile,
          performances: updatedperformances,
        };
        dispatch(updateProfile(updatedProfile));
      } else if (itemName === "email template" && idToDelete !== undefined && profile) {
        const updatedTemplates = profile.emailTemplates?.filter((t) => t.id !== idToDelete) ?? [];
        const updatedProfileData = await profileApiService.update({
          ...profile,
          emailTemplates: updatedTemplates,
        });
        dispatch(updateProfile(updatedProfileData));
      }
    } catch (error) {
      console.error(`Error deleting ${itemName}:`, error);
    }
  };
  if (!profile) return;
  return (
    <DetailsViewWrapper href="/profile">
      <DeleteModal
        open={openDeleteDialog}
        onOpenChange={setOpenDeleteDialog}
        onConfirm={onConfirmDelete}
        itemName={itemName}
      />
      <DetailsViewHeader
        title={profile?.companyName || "Profile"}
        subtitle={`${profile?.firstName} ${profile.lastName}`}
        icon={<CircleUser className="text-emerald-600 dark:text-emerald-400" size={32} />}
        entityId={profile.id}
        actionElements={
          <>
            {activeTab === "basic-information" && <EditButton href={`/profile/edit`} />}
            {activeTab === "email-settings" && <EditButton href={`/profile/edit/email-settings`} />}
            {activeTab === "account" && <EditButton href={`/profile/edit/preferences`} />}
          </>
        }
      />

      <DetailsTabs defaultTab={activeTab} onTabChange={handleTabChange}>
        <Tab name="Basic Information">
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
        </Tab>

        <Tab name="Performances">
          {profile.performances && profile.performances.length > 0 ? (
            <PerformanceViewSection
              performances={profile.performances}
              onDelete={(performanceId) => handleDelete("performance", performanceId)}
            />
          ) : (
            <p className="flex justify-center py-6">No performances</p>
          )}
          <AddSection label="performance" href={`/profile/edit/performances/new`} />
        </Tab>

        <Tab name="Email Templates">
          {profile.emailTemplates && profile.emailTemplates.length > 0 ? (
            <EmailTemplatesSection
              emailTemplates={profile.emailTemplates}
              onDelete={(templateId) => handleDelete("email template", templateId)}
            />
          ) : (
            <p className="flex justify-center py-6">No email templates</p>
          )}
          <AddSection label="email template" href={`/profile/edit/email-templates/new`} />
        </Tab>

        <Tab name="Email Settings">
          <OAuthEmailSection profile={profile} />
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-md text-sm text-blue-700 dark:text-blue-300">
            These values are used when contacting organisations.{" "}
            <Link
              href="/help/email-settings"
              target="_blank"
                  className="text-blue-600 hover:text-blue-800 underline"
            >
              View setup guide
            </Link>
          </div>
        </Tab>

        <Tab name="Account">
          <DetailsViewSection
            title="Preferences"
            icon={<Cog className="text-emerald-600 dark:text-emerald-400" />}
            data={getPreferencesInfo(profile)}
          />
          <div className="flex gap-4">
            <Button
              onClick={() => router.push("/profile/edit/change-password")}
              variant={"tertiary"}
            >
              Change Password
            </Button>
            <DeleteButton
              label="Delete account"
              variant={"outline"}
              className="text-red-500 border border-red-500 hover:text-red-400 hover:bg-background"
              onDelete={() => handleDelete("profile", profile.id)}
            />
          </div>
        </Tab>

        <Tab name="Reminders">
          <ProfileRemindersCard />
        </Tab>
      </DetailsTabs>
    </DetailsViewWrapper>
  );
};

export default ProfileView;
