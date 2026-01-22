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
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import { UploadStatCard } from "./UploadStatCard";

interface UploadStats {
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
      console.log("values", values, values.exce);
      const excelFile = values.excel as File;
      const stats = await organisationApiService.upload([excelFile]);
      setUploadStats(stats);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <>
      <FormHeader action={Action.UPLOAD} />
      <div className="flex flex-col max-w-xl mx-auto">
        <BasicForm
          form={form}
          formFields={formFields}
          onSubmit={onSubmit}
          isLoading={isLoading}
          action={Action.UPLOAD}
        />
      </div>
      {uploadStats && (
        <Card className="mt-8 max-w-xl mx-auto">
          <CardTitle className="text-emerald-600 text-xl p-4 border-b text-center">
            Upload Summary
          </CardTitle>
          <CardContent className="p-6">
            <div className="grid grid-cols-3 gap-4 mb-6">
              <UploadStatCard
                title="Festivals"
                imported={uploadStats.festivalsImported}
                skipped={uploadStats.festivalsSkipped}
              />
              <UploadStatCard
                title="Venues"
                imported={uploadStats.venuesImported}
                skipped={uploadStats.venuesSkipped}
              />
              <UploadStatCard
                title="Residencies"
                imported={uploadStats.residenciesImported}
                skipped={uploadStats.residenciesSkipped}
              />
            </div>

            {/* Errors */}
            {uploadStats.errors.length > 0 && (
              <div className="border-t pt-4">
                <p className="text-sm font-semibold text-red-600 dark:text-red-400 mb-3">
                  Import Errors ({uploadStats.errors.length})
                </p>
                <div className="rounded p-3 space-y-1 max-h-48 overflow-y-auto">
                  {uploadStats.errors.map((error, index) => (
                    <p key={index} className="text-sm text-red-700 dark:text-red-300">
                      {error}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </>
  );
};

export default UploadForm;
