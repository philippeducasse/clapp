"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import { createZodFormSchema } from "@/helpers/formHelper";
import BasicForm from "@/components/common/form/BasicForm";
import { getBugReportFormFields } from "@/components/page-components/bugReport/helpers/getBugReportFormFields";
import { BugReport, supportApiService } from "@/api/supportApiService";
import { Action } from "@/interfaces/Enums";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import FormHeader from "@/components/common/form/FormHeader";

const ReportBugPage = () => {
  const formFields = getBugReportFormFields();
  const formSchema = createZodFormSchema(formFields);

  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    mode: "onSubmit",
    defaultValues: {
      message: "",
      attachments: [],
    },
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      const bugReport: BugReport = {
        message: values.message as string,
        attachments: values.attachments as File[] | undefined,
      };
      await supportApiService.reportBug(bugReport);
      setSubmitted(true);
      form.reset();
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="container mx-auto p-6 max-w-2xl">
        <Link
          href="/help"
          className="text-emerald-600 hover:text-emerald-800 text-sm mb-4 inline-flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Help
        </Link>

        <Card className="border-l-4 border-l-emerald-500 bg-emerald-50">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <CheckCircle2 className="h-12 w-12 text-emerald-600" />
            </div>
            <CardTitle className="text-2xl text-emerald-700">
              Thank you for your feedback!
            </CardTitle>
            <CardDescription className="text-base text-emerald-800">
              Your bug report has been successfully submitted.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-700">
              We appreciate you helping us improve Circus Agent. Our team will review your report
              and investigate the issue.
            </p>
            <p className="text-sm text-gray-600">
              If you&apos;d like to report additional issues or need further assistance, feel free
              to submit another report or visit our help page.
            </p>
            <div className="flex gap-3 pt-4">
              <Button asChild className="bg-emerald-600 hover:bg-emerald-700">
                <Link href="/help">Back to Help</Link>
              </Button>
              <Button
                asChild
                variant="outline"
                onClick={() => {
                  setSubmitted(false);
                  form.reset();
                }}
              >
                <button>Report Another Issue</button>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <>
      <FormHeader action={Action.REPORT_BUG} />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        isLoading={isLoading}
        action={Action.CREATE}
        submitButtonLabel="Submit Bug Report"
      />
    </>
  );
};

export default ReportBugPage;
