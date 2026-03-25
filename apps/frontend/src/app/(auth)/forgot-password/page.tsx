import React from "react";
import Image from "next/image";
import ForgotPasswordForm from "@/components/page-components/auth/components/ForgotPasswordForm";
const page = () => {
  return (
    <div className="flex min-h-screen mt-24 justify-center bg-background">
      <div className="">
        <div className="flex justify-center gap-4 text-primary">
          <h1 className="font-clapp text-4xl">Clapp</h1>
          <Image src="/logo.png" width="60" height="60" alt="Clapping hands" />
        </div>
        <div className="w-full max-w-lg p-8">
          <ForgotPasswordForm />
        </div>
      </div>
    </div>
  );
};

export default page;
