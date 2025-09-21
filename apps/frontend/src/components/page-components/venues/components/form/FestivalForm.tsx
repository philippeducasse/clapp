"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useEffect, useState } from "react";
import { Venue } from "@/interfaces/entities/Venue";
import {
  createZodFormSchema,
  sanitizeFormData,
  getInitialValues,
} from "@/helpers/formHelper";
import { getVenueFormFields } from "../../helpers/getVenueFormFields";
import { venueApiService } from "@/api/venueApiService";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { updateVenue, selectVenue } from "@/redux/slices/venueSlice";
import { AppDispatch, RootState } from "@/redux/store";
import { refreshVenue } from "../../helpers/refreshVenue";
import { Skeleton } from "@/components/ui/skeleton";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action } from "@/interfaces/Enums";
import { EntityName } from "@/interfaces/Enums";
// import GenericButton from "@/components/common/buttons/GenericButton";

interface VenueFormProps {
  action: string;
}

const VenueForm = ({ action }: VenueFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();
  const venueId = Number(params?.id);
  const venue = useSelector((state: RootState) => selectVenue(state, venueId));
  const formFields = getVenueFormFields();
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const [initialDataLoaded, setInitialDataLoaded] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields, venue),
    mode: "onSubmit",
  });

  // Fetch venue data if not available
  useEffect(() => {
    if (!venue && venueId) {
      refreshVenue(venueId, dispatch);
      setInitialDataLoaded(true);
    }
  }, [venueId, venue, dispatch]);

  // Reset form when venue data changes (but only once)
  useEffect(() => {
    if (venue && initialDataLoaded) {
      console.log("resetting form data");
      form.reset(sanitizeFormData(venue));
      setInitialDataLoaded(false);
    }
  }, [venue, form, initialDataLoaded]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      if (action === Action.EDIT) {
        const updatedVenue = { ...values, id: venueId } as Venue;
        await venueApiService.updateVenue(updatedVenue);
        dispatch(updateVenue(updatedVenue));
        router.push(`/venues/${venue?.id}`);
      } else {
        const newVenue = await venueApiService.createVenue(values as Venue);
        router.push(`/venues/${newVenue?.id}`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!venue && venueId) {
    return <Skeleton />;
  }

  const onCancelHref = venueId ? `/venues/${venue?.id}` : "/venues";

  // const updateButton = GenericButton

  return (
    <>
      <FormHeader action={action} entityName={EntityName.VENUE} />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={onCancelHref}
        isLoading={isLoading}
        entity={venue}
      />
    </>
  );
};
export default VenueForm;
