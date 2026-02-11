"use client";

import { useState } from "react";
import { createZodFormSchema } from "@/helpers/formHelper";
import BasicForm from "@/components/common/form/BasicForm";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import FormHeader from "@/components/common/form/FormHeader";
import { getUploadFormFields } from "./helpers/getUploadFormFields";
import { Action } from "@/interfaces/Enums";
import { organisationApiService } from "@/api/organisationApiService";
import { UploadSummarySection } from "./uploadHelper";
import ImportingOrganizationsHelpPage from "@/app/(main)/help/importing-organizations/page";

export interface UploadStats {
  errors: string[];
  festivalsImported: number;
  festivalsSkipped: number;
  residenciesImported: number;
  residenciesSkipped: number;
  venuesImported: number;
  venuesSkipped: number;
}

const UploadForm = () => {
  const formFields = getUploadFormFields();
  const formSchema = createZodFormSchema(formFields);

  const [isLoading, setIsLoading] = useState(false);
  const [uploadStats, setUploadStats] = useState<UploadStats | null>(null);
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    mode: "onSubmit",
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      const excelFile = values.excel as File;
      const stats: UploadStats = await organisationApiService.upload([excelFile]);
      setUploadStats(stats);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <>
      <ImportingOrganizationsHelpPage showGoToUploadPage={false} />
      <div className="max-w-2xl mx-auto">
        <FormHeader action={Action.UPLOAD} />
        <BasicForm
          form={form}
          formFields={formFields}
          onSubmit={onSubmit}
          isLoading={isLoading}
          action={Action.UPLOAD}
        />
      </div>
      {uploadStats && <UploadSummarySection uploadStats={uploadStats} />}
    </>
  );
};

export default UploadForm;
