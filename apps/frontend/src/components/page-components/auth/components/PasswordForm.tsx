"use client";

import { useState } from "react";
import { createZodFormSchema, getInitialValues } from "@/helpers/formHelper";
import { profileApiService } from "@/api/profileApiService";
import BasicForm from "@/components/common/form/BasicForm";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { Action } from "@/interfaces/Enums";
import { getPasswordFormFields } from "../helpers/getPasswordFormFields";
import { useSearchParams } from "next/navigation";
import FormHeader from "@/components/common/form/FormHeader";
import { EntityName } from "@/interfaces/Enums";
const PasswordForm = ({ isReset = false }: { isReset?: boolean }) => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const formFields = getPasswordFormFields();
  const baseFormSchema = createZodFormSchema(formFields);
  const formSchema = baseFormSchema.refine((data) => data.newPassword === data.newPasswordConfirm, {
    message: "Passwords do not match",
    path: ["newPasswordConfirm"],
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
      const data = { token, newPassword: values.newPassword };
      await profileApiService.changePassword(data, isReset);
      router.push(isReset ? `/login` : "/profile");
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const formType = isReset ? "Reset password" : "Change password";

  return (
    <>
      <FormHeader action={Action.EDIT} entityName={EntityName.PROFILE} />
      <div className="max-w-lg mx-auto">
        <BasicForm
          form={form}
          formFields={formFields}
          onSubmit={onSubmit}
          isLoading={isLoading}
          submitButtonLabel={formType}
          action={Action.REGISTER}
        />
      </div>
    </>
  );
};

export default PasswordForm;
