import React from "react";
import Image from "next/image";
import PasswordForm from "@/components/page-components/auth/components/PasswordForm";
const page = () => {
  return (
    <div className="flex min-h-screen mt-24 justify-center bg-background">
      <div className="">
        <div className="flex justify-center gap-4 text-emerald-600">
          <h1 className="font-clapp text-4xl">Clapp</h1>
          <Image src="/logo.png" width="60" height="60" alt="Clapping hands" />
        </div>
        <div className="w-full max-w-xl p-8">
          <PasswordForm isReset />
        </div>
      </div>
    </div>
  );
};

export default page;
