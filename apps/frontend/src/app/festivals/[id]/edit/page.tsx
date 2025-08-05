"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Form } from "@/components/ui/form";
import { useFestival } from "@/context/FestivalContext";
import { useState } from "react";
import { Festival } from "@/interfaces/Festival";
import { getFestivalFormFields } from "../helpers/getFestivalFormFields";

import { createZodFormSchema, sanitizeFormData, createFormComponents } from "@/helpers/formHelper";
import festivalApiService from "@/api/festivalApiService";
import SubmitButton from "@/components/common/buttons/SubmitButton";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

const FestivalForm = () => {
  const { festival } = useFestival();
  const router = useRouter();
  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);

  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      await festivalApiService.updateFestival(values as Festival);
      toast.success("Festival has been updated successfully");
    } catch (error) {
      toast.error(`Error: Could not update festival : ${error}`);
      console.error(error);
    } finally {
      setIsLoading(false);
      router.push(`/festivals/${festival.id}`);
    }
  };

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: sanitizeFormData(festival),
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 max-w-3xl mx-auto mt-6">
        {createFormComponents(formFields, form)}
        <SubmitButton isLoading={isLoading} />
      </form>
    </Form>
  );
};

export default FestivalForm;
