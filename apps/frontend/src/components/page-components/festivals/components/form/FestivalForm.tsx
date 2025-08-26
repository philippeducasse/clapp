"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useEffect, useState } from "react";
import { Festival } from "@/interfaces/Festival";
import { createZodFormSchema, sanitizeFormData, getInitialValues } from "@/helpers/formHelper";
import { getFestivalFormFields } from "../../helpers/getFestivalFormFields";
import festivalApiService from "@/api/festivalApiService";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { updateFestival, selectFestival } from "@/redux/slices/festivalSlice";
import { AppDispatch, RootState } from "@/redux/store";
import { refreshFestival } from "../../helpers/refreshFestival";
import { Skeleton } from "@/components/ui/skeleton";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action } from "@/interfaces/Enums";

interface FestivalFormProps {
  action: string;
}

const FestivalForm = ({ action }: FestivalFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();
  const festivalId = Number(params?.id);
  const festival = useSelector((state: RootState) => selectFestival(state, festivalId));
  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const [initialDataLoaded, setInitialDataLoaded] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields, festival),
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
      if (action === Action.EDIT) {
        const updatedFestival = { ...values, id: festivalId } as Festival;
        await festivalApiService.updateFestival(updatedFestival);
        dispatch(updateFestival(updatedFestival));
        router.push(`/festivals/${festival?.id}`);
      } else {
        const newFestival = await festivalApiService.createFestival(values as Festival);
        router.push(`/festivals/${newFestival?.id}`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!festival && festivalId) {
    return <Skeleton />;
  }

  const onCancelHref = festivalId ? `/festivals/${festival?.id}` : "/festivals";

  return (
    <>
      <FormHeader action={action} entityName="festival" />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={onCancelHref}
        isLoading={isLoading}
        entity={festival}
      />
    </>
  );
};
export default FestivalForm;
