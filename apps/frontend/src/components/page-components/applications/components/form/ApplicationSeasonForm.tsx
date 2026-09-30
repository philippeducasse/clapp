"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useEffect, useState, useRef } from "react";
import {
  Application,
  ApplicationCreate,
  ApplicationSeason,
} from "@/interfaces/entities/Application";
import {
  createZodFormSchema,
  sanitizeFormData,
  getInitialValues,
} from "@/helpers/formHelper";
import { applicationApiService } from "@/api/applicationApiService";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/redux/store";
import { getApplicationSeasonFormFields } from "../../helpers/form/getApplicationSeasonFormFields";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action } from "@/interfaces/Enums";
import { EntityName } from "@/interfaces/Enums";
import { refreshApplication } from "../../helpers/refreshApplication";
import { selectProfile } from "@/redux/slices/authSlice";
import { profileApiService } from "@/api/profileApiService";

interface ApplicationSeasonFormProps {
  action: Action;
}

const ApplicationSeasonForm = ({ action }: ApplicationSeasonFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();
  const applicationSeasonId = Number(params?.id);
  const profile = useSelector((state: RootState) => selectProfile(state));
  const season = profile?.applicationSeasons?.find(
    (season) => season.id === applicationSeasonId,
  );
  const formFields = getApplicationSeasonFormFields();
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const initialDataLoadedRef = useRef(false);

  useEffect(() => {
    if (action !== Action.CREATE && !season) {
      refreshApplication(applicationSeasonId, dispatch);
    }
  }, [action, applicationSeasonId, season, dispatch]);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(
      formFields,
      season as unknown as Record<string, unknown>,
    ),
    mode: "onSubmit",
  });

  useEffect(() => {
    if (season && !initialDataLoadedRef.current) {
      form.reset(
        sanitizeFormData(season as unknown as Record<string, unknown>),
      );
      initialDataLoadedRef.current = true;
    }
  }, [season, form]);

  const onSubmit = async (values: { name: string }) => {
    setIsLoading(true);
    try {
      if (action === Action.EDIT) {
        const updatedApplicationSeason = {
          ...values,
          id: applicationSeasonId,
          profileId: profile?.id,
        } as ApplicationSeason;
        await profileApiService.update(updatedApplicationSeason);

        const selectedPerformances = performances.filter((p) =>
          (values.performanceIds as string[])?.includes(String(p.id)),
        );
        dispatch(
          updateApplication({
            ...updatedApplication,
            performances: selectedPerformances,
          }),
        );
        router.push(`/applications/${application?.id}`);
      } else {
        if (profile) {
          const application: ApplicationCreate = {
            ...values,
            profileId: profile.id,
            objectType: (values as Record<string, unknown>)
              .organisationType as string,
            objectId: (values as Record<string, unknown>)
              .organisation as number,
          };
          const newApplication = await applicationApiService.create(
            application as unknown as Application,
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

  const onCancelHref = applicationId
    ? `/applications/${application?.id}`
    : "/applications";

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
export default ApplicationSeasonForm;
