"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useFestival } from "@/context/FestivalContext";
import { useState } from "react";
import { Festival } from "@/interfaces/Festival";
import { getFestivalFormFields } from "../helpers/getFestivalFormFields";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { createZodFormSchema, sanitizeFormData, createFormComponents } from "@/helpers/formHelper";
import festivalApiService from "@/api/festivalApiService";
import SubmitButton from "@/components/common/SubmitButton";
import { toast } from "sonner";

export default function FestivalForm() {
  const festivalData = useFestival();

  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);

  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    console.log("Submitted data:", values);
    setIsLoading(true);
    try {
      await festivalApiService.updateFestival(values as Festival);
      toast.success("Festival has been updated successfully");
    } catch (error) {
      toast.error(`Error: Could not update festival : ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const [festival, setFestival] = useState<Festival>(festivalData);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: sanitizeFormData(festival),
  });

  const handleChange = (field: keyof Festival) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFestival((prev) => ({ ...prev, [field]: e.target.value }));
  };
  console.log({ form });
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 max-w-3xl mx-auto mt-6">
        {createFormComponents(formFields, form, formSchema, handleChange)}

        <SubmitButton isLoading={isLoading} />
      </form>
    </Form>
  );
}
