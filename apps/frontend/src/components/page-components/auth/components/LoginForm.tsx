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
const LoginForm = () => {
  const router = useRouter();

  const formFields = getAuthFormFields();
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
    <BasicForm
      form={form}
      formFields={formFields}
      onSubmit={onSubmit}
      onCancelHref={"index"}
      isLoading={isLoading}
      action={Action.LOGIN}
    />
  );
};

export default LoginForm;
