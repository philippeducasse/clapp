"use client";
import ContactsForm from "@/components/common/form/ContactsForm";
import { Festival } from "@/interfaces/entities/Festival";
import { selectFestival, updateFestival } from "@/redux/slices/festivalSlice";
import { festivalApiService } from "@/api/festivalApiService";
import { refreshFestival } from "../../helpers/refreshFestival";
import { EntityName } from "@/interfaces/Enums";
import { getContactFormFields } from "@/helpers/getContactFormFields";

interface FestivalContactsFormProps {
  action: string;
}

const FestivalContactsForm = ({ action }: FestivalContactsFormProps) => {
  return (
    <ContactsForm<Festival>
      action={action}
      entityName={EntityName.FESTIVAL}
      baseRoute="festivals"
      selectEntity={selectFestival}
      updateEntity={updateFestival}
      apiService={festivalApiService}
      refreshEntity={refreshFestival}
      getContactFormFields={getContactFormFields}
    />
  );
};

export default FestivalContactsForm;
