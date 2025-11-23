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
import {
  updatePerformance,
  selectPerformance,
  addPerformance,
} from "@/redux/slices/performanceSlice";
import { AppDispatch, RootState } from "@/redux/store";
import { Skeleton } from "@/components/ui/skeleton";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action, EntityName } from "@/interfaces/Enums";

interface PerformanceFormProps {
  action: string;
}

const PerformanceForm = ({ action }: PerformanceFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();

  const id = Number(params?.id);
  const profileId = action === Action.CREATE ? id : undefined;
  const performanceId = action === Action.EDIT ? id : undefined;

  const performance = useSelector((state: RootState) =>
    performanceId ? selectPerformance(state, performanceId) : undefined
  );
  const formFields = getPerformanceFormFields();
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const [initialDataLoaded, setInitialDataLoaded] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields, performance),
    mode: "onSubmit",
  });

  useEffect(() => {
    if (!performance && performanceId && action === Action.EDIT) {
      performanceApiService.getPerformance(performanceId).then(() => {
        setInitialDataLoaded(true);
      });
    }
  }, [performanceId, performance, action]);

  useEffect(() => {
    if (performance && initialDataLoaded) {
      form.reset(sanitizeFormData(performance));
      setInitialDataLoaded(false);
    }
  }, [performance, form, initialDataLoaded]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      // Clean up form data before sending to backend
      const cleanedData = prepareFormDataForSubmission(values, formFields);

      if (action === Action.EDIT && performanceId) {
        const updatedPerformance = { ...cleanedData, id: performanceId } as Performance;
        await performanceApiService.updatePerformance(updatedPerformance);
        dispatch(updatePerformance(updatedPerformance));
        router.push(`/profile`);
      } else if (action === Action.CREATE && profileId) {
        await performanceApiService.createPerformance(cleanedData as Performance);
        dispatch(addPerformance(cleanedData));
        router.push(`/profile`);
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

  const onCancelHref = `/profile`;

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
