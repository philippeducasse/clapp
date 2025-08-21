"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Form } from "@/components/ui/form";
import { useFestival } from "@/context/FestivalContext";
import { useState } from "react";
import { Festival } from "@/interfaces/Festival";
import { getFestivalFormFields } from "../../helpers/getFestivalFormFields";
import { createZodFormSchema, sanitizeFormData, createFormComponents } from "@/helpers/formHelper";
import festivalApiService from "@/api/festivalApiService";
import SubmitButton from "@/components/common/buttons/SubmitButton";
import { useRouter } from "next/navigation";
import BackButton from "@/components/common/buttons/BackButton";

const FestivalForm = () => {
  const { festival, setFestival } = useFestival();
  const router = useRouter();
  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);

  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    console.log("VALS:", values);
    setIsLoading(true);
    try {
      await festivalApiService.updateFestival(values as Festival);
      setFestival(values as Festival);
    } catch (error) {
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
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="w-full caption-bottom text-sm space-y-6 max-w-3xl mx-auto mt-6 border py-6 px-12 rounded-2xl shadow"
      >
        {createFormComponents(formFields, form)}
        <div className="flex justify-between mt-6">
          <BackButton href={`/festivals/${festival.id}`} />
          <SubmitButton isLoading={isLoading} />
        </div>
      </form>
    </Form>
  );
};

export default FestivalForm;
