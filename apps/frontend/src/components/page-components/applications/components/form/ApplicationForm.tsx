"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/redux/reducers";
import { selectFestival } from "@/redux/slices/festivalSlice";
import { useParams } from "next/navigation";
import { refreshFestival } from "@/components/page-components/festivals/helpers/refreshFestival";
import FormHeader from "@/components/common/form/FormHeader";
import { Action, EntityName } from "@/interfaces/Enums";
import BasicForm from "@/components/common/form/BasicForm";
import { createZodFormSchema, getInitialValues } from "@/helpers/formHelper";
import { getApplicationFormFields } from "../../helpers/form/getApplicationFormFields";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Bot } from "lucide-react";
import { festivalApiService } from "@/api/festivalApiService";
import { ApplicationCreate, ApplicationMethod } from "@/interfaces/entities/Application";
import { selectProfile } from "@/redux/slices/authSlice";
import { Festival } from "@/interfaces/entities/Festival";
import { Profile } from "@/interfaces/entities/Profile";
import { useRouter } from "next/navigation";
import { Dossier } from "@/interfaces/entities/Performance";

const ApplicationForm = () => {
  const params = useParams();
  const festivalId = Number(params.id);
  const festival = useSelector((state: RootState) => selectFestival(state, festivalId));
  const profile = useSelector((state: RootState) => selectProfile(state));
  const router = useRouter();
  const dispatch = useDispatch();
  const [isLoading, setIsLoading] = useState(false);
  const [dossiers, setDossiers] = useState<Dossier[]>([]);
  const [selectedPerformanceIds, setSelectedPerformanceIds] = useState<number[]>([]);
  const [applicationMethod, setApplicationMethod] = useState<
    ApplicationMethod.EMAIL | ApplicationMethod.FORM
  >(ApplicationMethod.EMAIL);
  const dossiersSetRef = useRef(false);

  const formFields = useMemo(() => {
    const performances = profile?.performances ?? [];
    return getApplicationFormFields(
      festival as Festival,
      performances,
      applicationMethod,
      profile as Profile,
      dossiers
    );
  }, [festival, applicationMethod, profile, dossiers]);

  const formSchema = useMemo(() => createZodFormSchema(formFields), [formFields]);

  const formKey = useMemo(() => `form-${dossiers.length}`, [dossiers]);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields),
    mode: "onSubmit",
  });

  const applicationMethodWatch = form.watch("applicationMethod") ?? "EMAIL";
  const performanceSelection = form.watch("performances") as string[];
  const language = form.watch("language") as string;
  const messageLength = form.watch("messageLength");

  useEffect(() => {
    setApplicationMethod(
      applicationMethodWatch as ApplicationMethod.EMAIL | ApplicationMethod.FORM
    );
  }, [applicationMethodWatch]);

  useEffect(() => {
    setSelectedPerformanceIds(performanceSelection.map((performanceId) => Number(performanceId)));
  }, [performanceSelection]);

  useEffect(() => {
    if (applicationMethod !== ApplicationMethod.EMAIL) return;

    const selectedPerformances = profile?.performances.filter((p) =>
      selectedPerformanceIds.includes(p.id)
    );

    const allDossierFiles =
      selectedPerformances?.flatMap((performance) => performance.dossiers ?? []) ?? [];

    setDossiers(allDossierFiles);
    dossiersSetRef.current = false;
  }, [selectedPerformanceIds, profile, applicationMethod]);

  useEffect(() => {
    if (dossiers.length > 0 && !dossiersSetRef.current) {
      const dossierIds = dossiers.map((d) => String(d.id));
      form.setValue("dossiers", dossierIds);
      dossiersSetRef.current = true;
    }
  }, [dossiers, form]);

  useEffect(() => {
    if (!festival) {
      refreshFestival(festivalId, dispatch);
    }
  }, [festivalId, festival, dispatch]);

  const onSubmit = async (values: Record<string, unknown>) => {
    setIsLoading(true);
    const { attachmentsSent, ...vals } = values;
    if (profile) {
      try {
        const applicationData = {
          ...vals,
          profileId: profile.id,
          objectType: "Festival",
          objectId: festivalId,
        };
        const response = await festivalApiService.apply(
          festivalId,
          applicationData as ApplicationCreate,
          attachmentsSent as File[],
          "attachments_sent"
        );
        if ("applicationId" in response) {
          router.push(`/applications/${response.applicationId}`);
        }
      } catch (error) {
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const generateEmail = () => {
    const handleClick = async () => {
      setIsLoading(true);
      if (profile) {
        const data = { profile, selectedPerformanceIds, language, messageLength };
        console.log(data);
        try {
          const { message } = await festivalApiService.generateEmail(festivalId, data);
          form.setValue("message", message);
        } catch (error) {
          console.error(`Failed to generate message: ${error}`);
        } finally {
          setIsLoading(false);
        }
      }
    };

    return (
      <Button variant="default" onClick={handleClick} disabled={isLoading}>
        <Bot />
        {isLoading ? "Generating..." : "Generate email"}
      </Button>
    );
  };

  return (
    <>
      <FormHeader action={Action.APPLY} entityName={EntityName.APPLICATION} />
      <BasicForm
        key={formKey}
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={`/festivals/${festival?.id}`}
        isLoading={isLoading}
        entity={festival}
        additionalActions={applicationMethod == ApplicationMethod.EMAIL ? generateEmail() : null}
        action={applicationMethod == ApplicationMethod.EMAIL ? Action.APPLY : Action.CREATE}
      />
    </>
  );
};

export default ApplicationForm;
