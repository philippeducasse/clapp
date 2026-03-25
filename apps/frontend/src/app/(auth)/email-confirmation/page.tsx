"use client";

import React from "react";
import Image from "next/image";
import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import ConfirmationMessage from "@/components/page-components/auth/components/ConfirmationMessage";

const EmailConfirmationPage = () => {
  const fallback = (
    <>
      <Skeleton className="h-6 mt-2 w-full" />
      <Skeleton className="h-6 mt-2 w-full" />
      <Skeleton className="h-6 mt-2 w-full" />
    </>
  );
  return (
    <div className="flex min-h-screen mt-24 justify-center bg-background">
      <div className="">
        <div className="flex justify-center gap-4 text-primary">
          <h1 className="font-clapp text-4xl">Clapp</h1>
          <Image src="/logo.png" width="60" height="60" alt="Clapping hands" />
        </div>
        <div className="w-full max-w-lg p-8">
          <Suspense fallback={fallback}>
            <ConfirmationMessage />
          </Suspense>
        </div>
      </div>
    </div>
  );
};

export default EmailConfirmationPage;
