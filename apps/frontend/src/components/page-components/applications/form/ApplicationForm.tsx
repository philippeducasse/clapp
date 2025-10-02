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
import { festivalApiService } from "@/api/festivalApiService";
import { Application } from "@/interfaces/entities/Application";
import { selectProfile } from "@/redux/slices/authSlice";
import { Profile } from "@/interfaces/entities/Profile";

const ApplicationForm = () => {
  const signature = `<br><br>
<table cellpadding="0" cellspacing="0" border="0" style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
  <tbody>
    <tr>
      <td style="padding-bottom: 10px;">
        <strong style="font-size: 16px;">Philippe Ducasse</strong><br>
        <span style="color: #666;">Philocircus | Circus Artist</span><br>
        <span style="color: #666;">Berlin, Germany</span>
      </td>
    </tr>
    <tr>
      <td style="padding-top: 10px; border-top: 2px solid #e0e0e0;">
        <a href="http://www.philippeducasse.com" style="color: #0066cc; text-decoration: none;">www.philippeducasse.com</a><br>
        <a href="mailto:info@philippeducasse.com" style="color: #0066cc; text-decoration: none;">info@philippeducasse.com</a>
      </td>
    </tr>
    <tr>
      <td style="padding-top: 10px;">
        <a href="https://instagram.com/philocircus" style="color: #0066cc; text-decoration: none; margin-right: 10px;">Instagram</a>
        <a href="https://facebook.com/philocircus" style="color: #0066cc; text-decoration: none; margin-right: 10px;">Facebook</a>
        <a href="https://www.youtube.com/@philocircus2242" style="color: #0066cc; text-decoration: none;">YouTube</a>
      </td>
    </tr>
  </tbody>
</table>`;

  const params = useParams();
  const festivalId = Number(params.id);
  const festival = useSelector((state: RootState) =>
    selectFestival(state, festivalId)
  );
  const profile = useSelector((state: RootState) => selectProfile(state));
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
    const { attachmentsSent, ...vals } = values;
    try {
      await festivalApiService.applyToFestival(
        festivalId,
        vals as Application,
        attachmentsSent as File[],
        "attachments_sent"
      );
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
        const { message } = await festivalApiService.generateEmail(
          festivalId,
          profile as Profile
        );
        form.setValue("message", message + signature);
      } catch (error) {
        console.error(`Failed to generate message: ${error}`);
      } finally {
        setIsLoading(false);
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
