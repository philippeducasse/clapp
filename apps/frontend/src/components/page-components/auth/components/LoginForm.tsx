"use client";

import { useState } from "react";
import {
  createZodFormSchema,
  getInitialValues,
  prepareFormDataForSubmission,
} from "@/helpers/formHelper";
import { profileApiService } from "@/api/profileApiService";
import BasicForm from "@/components/common/form/BasicForm";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { getAuthFormFields } from "../helpers/getAuthFormFields";
import { useRouter } from "next/navigation";
import { Action } from "@/interfaces/Enums";
import { Credentials } from "@/interfaces/api/ApiService";
const LoginForm = () => {
  const router = useRouter();

  const formFields = getAuthFormFields();
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields),
    mode: "onSubmit",
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      await profileApiService.login(prepareFormDataForSubmission(values) as unknown as Credentials);
      router.push(`/`);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col text-center">
      <h3 className="text-xl font-semibold">Login</h3>
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={"index"}
        isLoading={isLoading}
        action={Action.LOGIN}
        submitButtonLabel="Login"
      />
    </div>
  );
};

export default LoginForm;
