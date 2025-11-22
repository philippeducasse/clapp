"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useEffect, useState } from "react";
import { Application, ApplicationCreate } from "@/interfaces/entities/Application";
import { createZodFormSchema, sanitizeFormData, getInitialValues } from "@/helpers/formHelper";
import { applicationApiService } from "@/api/applicationApiService";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { updateApplication, selectApplication } from "@/redux/slices/applicationSlice";
import { AppDispatch, RootState } from "@/redux/store";
import { getManualApplicationFormFields } from "../../helpers/form/getManualApplicationFormFields";
import { Skeleton } from "@/components/ui/skeleton";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action } from "@/interfaces/Enums";
import { EntityName } from "@/interfaces/Enums";
import { selectAllPerformances } from "@/redux/slices/performanceSlice";
import { refreshApplication } from "../../helpers/refreshApplication";
import { selectProfile } from "@/redux/slices/authSlice";
import { fetchPerformances } from "@/redux/slices/performanceSlice";
import { useAppDispatch } from "@/redux/hook";

interface ManualApplicationFormProps {
  action: Action;
}

const ManualApplicationForm = ({ action }: ManualApplicationFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();
  const applicationId = Number(params?.id);
  const application = useSelector((state: RootState) => selectApplication(state, applicationId));
  const profile = useSelector((state: RootState) => selectProfile(state));
  const asyncDispatch = useAppDispatch();

  useEffect(() => {
    if (profile?.id) {
      asyncDispatch(fetchPerformances(profile.id));
    }
  }, [profile, asyncDispatch]);

  const performances = useSelector((state: RootState) => selectAllPerformances(state));
  const formFields = getManualApplicationFormFields(performances);
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const [initialDataLoaded, setInitialDataLoaded] = useState(false);
  useEffect(() => {
    if (action !== Action.CREATE && !application) {
      refreshApplication(applicationId, dispatch);
    }
  }, [action, applicationId, application, dispatch]);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields, application as unknown as Record<string, unknown>),
    mode: "onSubmit",
  });

  useEffect(() => {
    if (application && !initialDataLoaded) {
      const formData = {
        ...application,
        organisation:
          typeof application.organisation === "object"
            ? application.organisation?.id
            : application.organisation,
        performances: application.performances?.map((p) => p.id) ?? [],
      };

      form.reset(sanitizeFormData(formData as unknown as Record<string, unknown>));
      setInitialDataLoaded(true);
    }
  }, [application, form, initialDataLoaded]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      if (action === Action.EDIT) {
        const updatedApplication = {
          ...application,
          ...values,
          id: applicationId,
          profileId: profile?.id,
        } as Application;
        await applicationApiService.updateApplication(updatedApplication);
        dispatch(updateApplication(updatedApplication));
        router.push(`/applications/${application?.id}`);
      } else {
        if (profile) {
          const application: ApplicationCreate = {
            ...values,
            profileId: profile.id,
            objectType: (values as Record<string, unknown>).organisationType as string,
            objectId: (values as Record<string, unknown>).organisation as number,
          };
          const newApplication = await applicationApiService.createApplication(
            application as unknown as Application
          );
          router.push(`/applications/${newApplication?.id}`);
        }
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!application && applicationId) {
    return <Skeleton />;
  }

  const onCancelHref = applicationId ? `/applications/${application?.id}` : "/applications";

  return (
    <>
      <FormHeader action={action} entityName={EntityName.APPLICATION} />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={onCancelHref}
        isLoading={isLoading}
        entity={application}
        action={action}
      />
    </>
  );
};
export default ManualApplicationForm;
