"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { useEffect, useState } from "react";
import { Festival } from "@/interfaces/Festival";
import { createZodFormSchema, sanitizeFormData, getFestivalControlledInputs } from "@/helpers/formHelper";
import { getFestivalFormFields } from "../../helpers/getFestivalFormFields";
import festivalApiService from "@/api/festivalApiService";
import SubmitButton from "@/components/common/buttons/SubmitButton";
import BackButton from "@/components/common/buttons/BackButton";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { updateFestival, selectFestival } from "@/redux/slices/festivalSlice";
import { AppDispatch, RootState } from "@/redux/store";
import { refreshFestival } from "../../helpers/refreshFestival";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";

interface FestivalFormProps {
  showLabels: boolean;
}

const FestivalForm = ({ showLabels }: FestivalFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();
  const festivalId = Number(params?.id);
  const festival = useSelector((state: RootState) => selectFestival(state, festivalId));
  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const [initialDataLoaded, setInitialDataLoaded] = useState(false);

  // Create initial form values
  const getInitialValues = () => {
    if (festival) {
      return sanitizeFormData(festival);
    }

    // If no festival, create empty default values for all fields
    const emptyValues = formFields.reduce((acc, field) => {
      acc[field.fieldName] = field.type === ControlledFormElementType.BOOLEAN ? false : "";
      return acc;
    }, {} as Record<string, unknown>);

    return emptyValues;
  };

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(),
    mode: "onSubmit",
  });

  // Fetch festival data if not available
  useEffect(() => {
    if (!festival && festivalId) {
      refreshFestival(festivalId, dispatch);
      setInitialDataLoaded(true);
    }
  }, [festivalId, festival, dispatch]);

  // Reset form when festival data changes (but only once)
  useEffect(() => {
    if (festival && initialDataLoaded) {
      console.log("resetting form data");
      form.reset(sanitizeFormData(festival));
      setInitialDataLoaded(false);
    }
  }, [festival, form, initialDataLoaded]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      const updatedFestival = { ...values, id: festivalId } as Festival;
      await festivalApiService.updateFestival(updatedFestival);
      dispatch(updateFestival(updatedFestival));
      if (festival) {
        router.push(`/festivals/${festival.id}`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!festival && festivalId) {
    return <div>Loading...</div>;
  }

  if (!festival && !festivalId) {
    return <div>Festival not found</div>;
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="w-full caption-bottom text-sm space-y-6 max-w-3xl mx-auto mt-6 border py-6 px-12 rounded-2xl shadow"
      >
        {formFields.map((formField) => (
          <FormField
            control={form.control}
            name={formField.fieldName as string}
            key={formField.fieldName}
            render={({ field }) => (
              <FormItem>
                {showLabels && <FormLabel>{formField.label}</FormLabel>}
                <FormControl>{getFestivalControlledInputs(formField, field, showLabels)}</FormControl>
                {showLabels && formField.helpText && <FormDescription>{formField.helpText}</FormDescription>}
                <FormMessage />
              </FormItem>
            )}
          />
        ))}
        <div className="flex justify-between mt-6">
          <BackButton href={`/festivals/${festival?.id || ""}`} />
          <SubmitButton isLoading={isLoading} />
        </div>
      </form>
    </Form>
  );
};
export default FestivalForm;
