"use client";
import ContactsForm from "@/components/common/form/ContactsForm";
import { Venue } from "@/interfaces/entities/Venue";
import { selectVenue, updateVenue } from "@/redux/slices/venueSlice";
import { venueApiService } from "@/api/venueApiService";
import { refreshVenue } from "../../helpers/refreshVenue";
import { EntityName } from "@/interfaces/Enums";
import { getContactFormFields } from "@/helpers/getContactFormFields";

interface VenueContactsFormProps {
  action: string;
}

const VenueContactsForm = ({ action }: VenueContactsFormProps) => {
  return (
    <ContactsForm<Venue>
      action={action}
      entityName={EntityName.VENUE}
      baseRoute="venues"
      selectEntity={selectVenue}
      updateEntity={updateVenue}
      apiService={venueApiService}
      refreshEntity={refreshVenue}
      getContactFormFields={getContactFormFields}
    />
  );
};

export default VenueContactsForm;
