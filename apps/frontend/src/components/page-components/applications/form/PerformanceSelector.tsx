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

interface PerformanceSelectorProps {
  performances: Performance[];
}

const PerformanceSelector = ({ performances }: PerformanceSelectorProps) => {
  const formFields = getPerformanceFormFields(performances);
  const formSchema = createZodFormSchema(formFields);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields),
    mode: "onSubmit",
  });

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="w-full caption-bottom text-sm space-y-6 max-w-4xl mx-auto mt-6 border py-6 px-12 rounded-2xl shadow"
      >
        {formFields.map((formField) => (
          <FormField
            control={form.control}
            name={formField.fieldName as string}
            key={formField.fieldName}
            render={({ field }) => (
              <FormItem>
                {!formField.hidden && (
                  <FormLabel className="text-emerald-700 dark:text-emerald-400">
                    {formField.label}
                  </FormLabel>
                )}
                <FormControl className="">
                  {getControlledInputs(formField, field, true)}
                </FormControl>
                <FormDescription>{formField.helpText}</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        ))}
      </form>
    </Form>
  );
};

export default PerformanceSelector;
