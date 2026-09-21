"use client";
import { Venue } from "@/interfaces/entities/Venue";
import { getVenueFormFields } from "../../helpers/form/getVenueFormFields";
import { venueApiService } from "@/api/venueApiService";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { updateVenue, selectVenue, setVenue } from "@/redux/slices/venueSlice";
import { AppDispatch, RootState } from "@/redux/store";
import { refreshVenue } from "../../helpers/refreshVenue";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action } from "@/interfaces/Enums";
import { EntityName } from "@/interfaces/Enums";
import { useEntityForm } from "@/hooks/useEntityForm";

interface VenueFormProps {
  action: Action;
}

const VenueBasicInfoForm = ({ action }: VenueFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();
  const venueId = Number(params?.id);
  const venue = useSelector((state: RootState) => selectVenue(state, venueId || -1));
  const formFields = getVenueFormFields();
  const { form, isLoading, setIsLoading } = useEntityForm(venue, venueId, formFields, refreshVenue, dispatch);

  const onSubmit = async (values: Record<string, unknown>) => {
    setIsLoading(true);
    try {
      if (action === Action.EDIT) {
        const updatedVenue = { ...values, id: venueId } as Venue;
        await venueApiService.update(updatedVenue);
        dispatch(updateVenue(updatedVenue));
        router.push(`/venues/${venue?.id}`);
      } else {
        const tempVenue = { ...values, id: -1 };
        dispatch(setVenue(tempVenue as Venue));
        router.push(`/venues/create/contact`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const onCancelHref = venueId ? `/venues/${venue?.id}` : "/venues";
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
        action={action}
        formTitle="Basic Information"
        submitButtonLabel={action === Action.CREATE ? "Next" : "Save"}
        formSubtitle={
          action === Action.CREATE
            ? "Please provide basic venue information. You will provide contact information next."
            : ""
        }
      />
    </>
  );
};
export default VenueBasicInfoForm;
