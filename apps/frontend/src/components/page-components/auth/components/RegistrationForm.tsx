"use client";

import { useState } from "react";
import { createZodFormSchema, getInitialValues } from "@/helpers/formHelper";
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
  const baseFormSchema = createZodFormSchema(formFields);
  const formSchema = baseFormSchema.refine((data) => data.password === data.passwordConfirm, {
    message: "Passwords do not match",
    path: ["passwordConfirm"],
  });
  const [isLoading, setIsLoading] = useState(false);
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields),
    mode: "onSubmit",
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      await profileApiService.register(values);
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
        isLoading={isLoading}
        submitButtonLabel="Register"
        action={Action.REGISTER}
      />
    </div>
  );
};

export default RegistrationForm;
