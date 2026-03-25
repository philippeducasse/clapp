"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/redux/reducers";
import { selectFestival } from "@/redux/slices/festivalSlice";
import { selectResidency } from "@/redux/slices/residencySlice";
import { selectVenue } from "@/redux/slices/venueSlice";
import { useParams } from "next/navigation";
import { refreshFestival } from "@/components/page-components/festivals/helpers/refreshFestival";
import { refreshResidency } from "@/components/page-components/residencies/helpers/refreshResidency";
import { refreshVenue } from "@/components/page-components/venues/helpers/refreshVenue";
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
import { residencyApiService } from "@/api/residencyApiService";
import { venueApiService } from "@/api/venueApiService";
import { ApplicationCreate, ApplicationMethod } from "@/interfaces/entities/Application";
import { selectProfile } from "@/redux/slices/authSlice";
import { Profile } from "@/interfaces/entities/Profile";
import { useRouter } from "next/navigation";
import { Dossier } from "@/interfaces/entities/Performance";

interface ApplicationFormProps {
  entityName: EntityName.FESTIVAL | EntityName.RESIDENCY | EntityName.VENUE;
}

const ENTITY_CONFIG = {
  [EntityName.FESTIVAL]: { objectType: "Festival", basePath: "festivals" },
  [EntityName.RESIDENCY]: { objectType: "Residency", basePath: "residencies" },
  [EntityName.VENUE]: { objectType: "Venue", basePath: "venues" },
};

const ApplicationForm = ({ entityName }: ApplicationFormProps) => {
  const params = useParams();
  const entityId = Number(params.id);

  const festival = useSelector((state: RootState) => selectFestival(state, entityId));
  const residency = useSelector((state: RootState) => selectResidency(state, entityId));
  const venue = useSelector((state: RootState) => selectVenue(state, entityId));

  const entity =
    entityName === EntityName.FESTIVAL
      ? festival
      : entityName === EntityName.RESIDENCY
        ? residency
        : venue;

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

  const config = ENTITY_CONFIG[entityName];

  const formFields = useMemo(() => {
    const performances = profile?.performances ?? [];
    const emailTemplates = profile?.emailTemplates ?? [];
    return getApplicationFormFields(
      entity,
      performances,
      applicationMethod,
      profile as Profile,
      dossiers,
      emailTemplates,
    );
  }, [entity, applicationMethod, profile, dossiers]);

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
  const selectedTemplateId = form.watch("emailTemplate") as string;

  useEffect(() => {
    setApplicationMethod(
      applicationMethodWatch as ApplicationMethod.EMAIL | ApplicationMethod.FORM,
    );
  }, [applicationMethodWatch]);

  useEffect(() => {
    setSelectedPerformanceIds(performanceSelection.map((performanceId) => Number(performanceId)));
  }, [performanceSelection]);

  useEffect(() => {
    if (applicationMethod !== ApplicationMethod.EMAIL) return;

    const selectedPerformances = profile?.performances.filter((p) =>
      selectedPerformanceIds.includes(p.id),
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
    if (!entity) {
      if (entityName === EntityName.FESTIVAL) refreshFestival(entityId, dispatch);
      else if (entityName === EntityName.RESIDENCY) refreshResidency(entityId, dispatch);
      else refreshVenue(entityId, dispatch);
    }
  }, [entityId, entity, entityName, dispatch]);

  useEffect(() => {
    if (!entity?.contacts?.length) return;
    const emails = entity.contacts.map((c) => c.email).filter(Boolean);
    if (emails.length > 0) {
      form.setValue("recipients", emails);
    }
  }, [entity, form]);

  useEffect(() => {
    if (!selectedTemplateId || applicationMethod !== ApplicationMethod.EMAIL) return;

    const template = profile?.emailTemplates?.find((t) => t.id === Number(selectedTemplateId));
    if (!template) return;

    form.setValue("message", template.content);
  }, [selectedTemplateId, applicationMethod, profile, form]);

  const onSubmit = async (values: Record<string, unknown>) => {
    setIsLoading(true);
    const { attachmentsSent, ...vals } = values;
    if (profile) {
      try {
        const applicationData = {
          ...vals,
          profileId: profile.id,
          objectType: config.objectType,
          objectId: entityId,
        };

        const apiService =
          entityName === EntityName.FESTIVAL
            ? festivalApiService
            : entityName === EntityName.RESIDENCY
              ? residencyApiService
              : venueApiService;

        const response = (await apiService.apply(
          entityId,
          applicationData as ApplicationCreate,
          attachmentsSent as File[],
          "attachments_sent",
        )) as unknown as { applicationId?: number };

        if (response && "applicationId" in response) {
          router.push(`/applications/${response.applicationId}`);
        }
      } catch (error) {
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const generateEmail = useCallback(() => {
    const handleClick = async () => {
      setIsLoading(true);
      if (profile) {
        const data = { profile, selectedPerformanceIds, language, messageLength };
        try {
          let message: string;
          if (entityName === EntityName.FESTIVAL) {
            const result = await festivalApiService.generateEmail(entityId, data);
            message = result.message;
          } else if (entityName === EntityName.RESIDENCY) {
            const result = await residencyApiService.generateEmail(entityId);
            message = result.message;
          } else {
            const result = await venueApiService.generateEmail(entityId);
            message = result.message;
          }
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
  }, [
    profile,
    selectedPerformanceIds,
    language,
    messageLength,
    isLoading,
    form,
    entityId,
    entityName,
  ]);

  return (
    <>
      <FormHeader action={Action.APPLY} entityName={EntityName.APPLICATION} />
      <BasicForm
        key={formKey}
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={`/${config.basePath}/${entity?.id}`}
        isLoading={isLoading}
        entity={entity}
        additionalActions={applicationMethod == ApplicationMethod.EMAIL ? generateEmail() : null}
        action={applicationMethod == ApplicationMethod.EMAIL ? Action.APPLY : Action.CREATE}
      />
    </>
  );
};

export default ApplicationForm;
