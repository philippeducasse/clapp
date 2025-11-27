"use client";

import { useState } from "react";
import { createZodFormSchema } from "@/helpers/formHelper";
import { profileApiService } from "@/api/profileApiService";
import BasicForm from "@/components/common/form/BasicForm";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { getAuthFormFields } from "../helpers/getAuthFormFields";
import { useRouter } from "next/navigation";
import { Action } from "@/interfaces/Enums";

const IS_REGISRATION = true;
const RegistrationForm = () => {
  const router = useRouter();
  const formFields = getAuthFormFields(IS_REGISRATION);
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    mode: "onSubmit",
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      await profileApiService.createProfile(values);
      router.push(`/login`);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="flex flex-col text-center">
      <h3 className="text-xl font-semibold">Register</h3>
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={"index"}
        isLoading={isLoading}
        submitButtonLabel="Register"
        action={Action.REGISTER}
      />
    </div>
  );
};

export default RegistrationForm;
