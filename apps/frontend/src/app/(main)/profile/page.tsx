import React, { Suspense } from "react";
import ProfileView from "@/components/page-components/profile/components/ProfileView";
import DetailsViewSkeleton from "@/components/common/skeletons/DetailsViewSkeleton";

const ProfilePage = () => {
  return (
    <Suspense fallback={<DetailsViewSkeleton />}>
      <ProfileView />
    </Suspense>
  );
};

export default ProfilePage;
