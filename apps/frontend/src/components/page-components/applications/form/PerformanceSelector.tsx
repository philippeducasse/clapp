import React from "react";
import {
  Form,
  FormItem,
  FormLabel,
  FormControl,
  FormField,
} from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { createZodFormSchema, getInitialValues } from "@/helpers/formHelper";
import { Performance } from "@/interfaces/entities/Performance";
import GenericButton from "@/components/common/buttons/GenericButton";

interface PerformanceSelectorProps {
  performances: Performance[];
}

const PerformanceSelector = ({ performances }: PerformanceSelectorProps) => {
  // const formFields = getPerformanceFormFields(performances);
  // const formSchema = createZodFormSchema(formFields);

  // const form = useForm<z.infer<typeof formSchema>>({
  //   resolver: zodResolver(formSchema),
  //   defaultValues: getInitialValues(formFields),
  //   mode: "onSubmit",
  // });
  const selectPerformance = (performanceId: number) => {
    console.log(performanceId);
  };
  return (
    <div
      // onSubmit={form.handleSubmit(onSubmit)}
      className="w-full caption-bottom text-sm space-y-6 max-w-4xl mx-auto mt-6 border py-6 px-12 rounded-2xl shadow"
    >
      {performances.map((performance) => (
        <GenericButton
          label={performance.performanceTitle}
          onClick={() => selectPerformance(performance.id)}
        />
      ))}
    </div>
  );
};

export default PerformanceSelector;
