"use client";
import ContactsForm from "@/components/common/form/ContactsForm";
import { Residency } from "@/interfaces/entities/Residency";
import { selectResidency, updateResidency } from "@/redux/slices/residencySlice";
import { residencyApiService } from "@/api/residencyApiService";
import { refreshResidency } from "../../helpers/refreshResidency";
import { EntityName } from "@/interfaces/Enums";
import { getContactFormFields } from "@/helpers/getContactFormFields";

interface ResidencyContactsFormProps {
  action: string;
}

const ResidencyContactsForm = ({ action }: ResidencyContactsFormProps) => {
  return (
    <ContactsForm<Residency>
      action={action}
      entityName={EntityName.RESIDENCY}
      baseRoute="residencies"
      selectEntity={selectResidency}
      updateEntity={updateResidency}
      apiService={residencyApiService}
      refreshEntity={refreshResidency}
      getContactFormFields={getContactFormFields}
    />
  );
};

export default ResidencyContactsForm;
