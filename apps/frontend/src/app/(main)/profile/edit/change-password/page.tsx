import React from "react";
import PasswordForm from "@/components/page-components/auth/components/PasswordForm";
import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";

const EditProfilePage = () => {
  return (
    <Suspense
      fallback={
        <>
          <Skeleton className="h-6 mt-2 w-full" />
          <Skeleton className="h-6 mt-2 w-full" />
          <Skeleton className="h-6 mt-2 w-full" />
        </>
      }
    >
      <PasswordForm />
    </Suspense>
  );
};

export default EditProfilePage;
