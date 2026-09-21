"use client";

import { useState, useRef, useEffect } from "react";
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
  const summaryRef = useRef<HTMLDivElement>(null);
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    mode: "onSubmit",
  });

  useEffect(() => {
    if (uploadStats && summaryRef.current) {
      summaryRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [uploadStats]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      const excelFile = values.excel as File;
      const taskId = await organisationApiService.upload([excelFile]);
      const stats = await organisationApiService.pollTask(taskId);

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
      {uploadStats && (
        <div ref={summaryRef}>
          <UploadSummarySection uploadStats={uploadStats} />
        </div>
      )}
    </>
  );
};

export default UploadForm;
