"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useEffect, useState, useRef } from "react";
import { ApplicationSeason } from "@/interfaces/entities/Application";
import {
  createZodFormSchema,
  sanitizeFormData,
  getInitialValues,
  prepareFormDataForSubmission,
} from "@/helpers/formHelper";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "@/redux/store";
import { getApplicationSeasonFormFields } from "../../helpers/form/getApplicationSeasonFormFields";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Skeleton } from "@/components/ui/skeleton";
import { Action, EntityName } from "@/interfaces/Enums";
import { selectProfile, updateProfile } from "@/redux/slices/authSlice";
import { profileApiService } from "@/api/profileApiService";
import DeleteButton from "@/components/common/buttons/DeleteButton";
import { DeleteModal } from "@/components/common/modals/DeleteModal";

interface ApplicationSeasonFormProps {
  action: Action;
}

const ApplicationSeasonForm = ({ action }: ApplicationSeasonFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();
  const seasonId =
    action === Action.EDIT ? Number(params?.seasonId) : undefined;
  const profile = useSelector((state: RootState) => selectProfile(state));
  const season = profile?.applicationSeasons?.find((s) => s.id === seasonId);
  const formFields = getApplicationSeasonFormFields();
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const formInitializedRef = useRef(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(
      formFields,
      season as unknown as Record<string, unknown>,
    ),
    mode: "onSubmit",
  });

  useEffect(() => {
    if (season && action === Action.EDIT && !formInitializedRef.current) {
      form.reset(
        sanitizeFormData(
          season as unknown as Record<string, unknown>,
          formFields,
        ),
      );
      formInitializedRef.current = true;
    }
  }, [season, action, form, formFields]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    if (!profile) return;
    setIsLoading(true);
    try {
      const cleanedData = prepareFormDataForSubmission(
        values,
        formFields,
      ) as Omit<ApplicationSeason, "id">;
      const existingSeasons = profile.applicationSeasons ?? [];

      let updatedSeasons: Partial<ApplicationSeason>[];
      if (action === Action.EDIT && seasonId) {
        updatedSeasons = existingSeasons.map((s) =>
          s.id === seasonId ? { ...s, ...cleanedData, id: seasonId } : s,
        );
      } else {
        updatedSeasons = [...existingSeasons, { ...cleanedData }];
      }

      const updatedProfile = await profileApiService.update({
        ...profile,
        applicationSeasons: updatedSeasons as ApplicationSeason[],
      });
      dispatch(updateProfile(updatedProfile));
      router.push(`/profile#applications`);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const onDelete = async () => {
    if (!profile || !seasonId) return;
    const updatedProfile = await profileApiService.update({
      ...profile,
      applicationSeasons: (profile.applicationSeasons ?? []).filter(
        (s) => s.id !== seasonId,
      ),
    });
    dispatch(updateProfile(updatedProfile));
    router.push(`/profile#applications`);
  };

  if (!season && seasonId && action === Action.EDIT) {
    return <Skeleton />;
  }

  return (
    <>
      <FormHeader action={action} entityName={EntityName.APPLICATION_SEASON} />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={`/profile#applications`}
        isLoading={isLoading}
        entity={season}
        additionalActions={
          action === Action.EDIT && season ? (
            <DeleteButton onDelete={() => setIsDeleteModalOpen(true)} />
          ) : undefined
        }
      />
      <DeleteModal
        open={isDeleteModalOpen}
        onOpenChange={setIsDeleteModalOpen}
        onConfirm={onDelete}
        itemName="season"
      />
    </>
  );
};
export default ApplicationSeasonForm;
