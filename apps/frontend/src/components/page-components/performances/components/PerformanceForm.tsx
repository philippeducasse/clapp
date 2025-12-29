"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useEffect, useState } from "react";
import { Performance } from "@/interfaces/entities/Performance";
import {
  createZodFormSchema,
  sanitizeFormData,
  getInitialValues,
  prepareFormDataForSubmission,
} from "@/helpers/formHelper";
import { getPerformanceFormFields } from "../helpers/form/getPerformanceFormFields";
import { performanceApiService } from "@/api/performanceApiService";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/redux/store";
import { Skeleton } from "@/components/ui/skeleton";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action, EntityName } from "@/interfaces/Enums";
import { selectProfile, addPerformance, updatePerformance } from "@/redux/slices/authSlice";

interface PerformanceFormProps {
  action: string;
}

const PerformanceForm = ({ action }: PerformanceFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();

  const performanceId = action === Action.EDIT ? Number(params?.performanceId) : undefined;
  const profile = useSelector((state: RootState) => selectProfile(state));
  const performance = profile?.performances.find((p) => p.id === performanceId);
  const formFields = getPerformanceFormFields();
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const [formInitialized, setFormInitialized] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields, performance),
    mode: "onSubmit",
  });

  useEffect(() => {
    if (performance && action === Action.EDIT && !formInitialized) {
      form.reset(sanitizeFormData(performance, formFields));
      setFormInitialized(true);
    }
  }, [performance, action, formInitialized, form, formFields]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      const cleanedData = prepareFormDataForSubmission(values, formFields);
      console.log({ cleanedData, values });
      if (action === Action.EDIT && performanceId) {
        const updatedPerformance = await performanceApiService.update({
          ...cleanedData,
          id: performanceId,
        } as Performance);
        dispatch(updatePerformance(updatedPerformance));
        router.push(`/profile#performances`);
      } else if (action === Action.CREATE && profile) {
        const newPerformance = await performanceApiService.create({
          ...cleanedData,
          profile: profile.id,
        } as Performance);
        dispatch(addPerformance(newPerformance));
        router.push(`/profile#performances`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!performance && performanceId && action === Action.EDIT) {
    return <Skeleton />;
  }

  const onCancelHref = `/profile#performances`;

  return (
    <>
      <FormHeader action={action} entityName={EntityName.PERFORMANCE} />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={onCancelHref}
        isLoading={isLoading}
        entity={performance}
      />
    </>
  );
};

export default PerformanceForm;
