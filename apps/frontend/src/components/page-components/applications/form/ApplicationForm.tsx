"use client";

import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/redux/reducers";
import {
  selectFestival,
  setSelectedFestival,
} from "@/redux/slices/festivalSlice";
import { useParams } from "next/navigation";
import { refreshFestival } from "../../festivals/helpers/refreshFestival";
import FormHeader from "@/components/common/form/FormHeader";
import { Action, EntityName } from "@/interfaces/Enums";
import BasicForm from "@/components/common/form/BasicForm";
import { createZodFormSchema, getInitialValues } from "@/helpers/formHelper";
import { getApplicationFormFields } from "../helpers/getApplicationFormFields";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Bot } from "lucide-react";
import festivalApiService from "@/api/festivalApiService";
import { Application } from "@/interfaces/entities/Application";

const ApplicationForm = () => {
  const params = useParams();
  const festivalId = Number(params.id);
  const festival = useSelector((state: RootState) =>
    selectFestival(state, festivalId)
  );
  const dispatch = useDispatch();
  const [isLoading, setIsLoading] = useState(false);
  const formFields = getApplicationFormFields();
  const formSchema = createZodFormSchema(formFields);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields),
    mode: "onSubmit",
  });

  useEffect(() => {
    if (!festival) {
      refreshFestival(festivalId, dispatch);
    } else {
      dispatch(setSelectedFestival(festival));
    }
  }, [festivalId, festival, dispatch]);

  const onSubmit = async (values: Application) => {
    setIsLoading(true);
    console.log("VALS:", values);
    const { attachmentsSent, ...vals } = values;
    try {
      const application = await festivalApiService.applyToFestival(
        festivalId,
        vals as Application,
        attachmentsSent as File[],
        "attachments_sent"
      );
      console.log("RESPONSE:", { application });
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateEmail = () => {
    const handleClick = async () => {
      setIsLoading(true);
      try {
        const { message } = await festivalApiService.generateEmail(festivalId);
        form.setValue("message", message);
      } catch (error) {
        console.error(`Failed to generate message: ${error}`);
      } finally {
        setIsLoading(false);
      }
    };

    console.log(form.formState);

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
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={`/festivals/${festival?.id}`}
        isLoading={isLoading}
        entity={festival}
        additionalActions={generateEmail()}
        action={Action.APPLY}
      />
    </>
  );
};

export default ApplicationForm;
