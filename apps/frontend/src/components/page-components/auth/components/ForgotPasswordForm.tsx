"use client";

import { useState } from "react";
import { createZodFormSchema, getInitialValues } from "@/helpers/formHelper";
import { profileApiService } from "@/api/profileApiService";
import BasicForm from "@/components/common/form/BasicForm";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Action } from "@/interfaces/Enums";
import { getForgotPasswordFormFields } from "../helpers/getForgotPasswordFormFields";

const ForgotPasswordForm = () => {
  const formFields = getForgotPasswordFormFields();
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
      await profileApiService.forgotPassword(values);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="flex flex-col">
      <h3 className="text-xl text-center">Reset password</h3>
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        isLoading={isLoading}
        submitButtonLabel="Reset password"
        action={Action.REGISTER}
      />
    </div>
  );
};

export default ForgotPasswordForm;
