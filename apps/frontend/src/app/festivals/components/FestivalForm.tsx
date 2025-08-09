"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Form } from "@/components/ui/form";
import { useFestival } from "@/context/FestivalContext";
import { useState } from "react";
import { Festival } from "@/interfaces/Festival";
import { getFestivalFormFields } from "../[id]/helpers/getFestivalFormFields";
import { cn } from "@/lib/utils";
import { createZodFormSchema, sanitizeFormData, createFormComponents } from "@/helpers/formHelper";
import festivalApiService from "@/api/festivalApiService";
import SubmitButton from "@/components/common/buttons/SubmitButton";
import { useRouter } from "next/navigation";
import BackButton from "@/components/common/buttons/BackButton";

interface FestivalFormProps {
  enrichedFestival?: Festival;
  className?: string;
  backButton?: boolean;
  showLabels?: boolean;
}

const FestivalForm = ({ enrichedFestival, className, backButton = true, showLabels = true }: FestivalFormProps) => {
  const { festival, setFestival } = useFestival();
  const router = useRouter();
  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);

  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
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

  const relevantFestival = enrichedFestival ?? festival;

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),

    defaultValues: sanitizeFormData(relevantFestival),
  });

  console.log(showLabels);

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className={cn("w-full caption-bottom text-sm", className)}>
        {createFormComponents(formFields, form, showLabels)}
        <div className="flex justify-between">
          {backButton && <BackButton href={`/festivals/${festival.id}`} />}
          <SubmitButton isLoading={isLoading} />
        </div>
      </form>
    </Form>
  );
};

export default FestivalForm;
