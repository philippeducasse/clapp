import { Dispatch, SetStateAction } from "react";
import { Venue } from "@/interfaces/entities/Venue";
import { getVenueFormFields } from "../../helpers/form/getVenueFormFields";
import GenericDiffForm from "@/components/common/form/GenericDiffForm";

interface VenueDiffFormProps {
  updated: Venue;
  changedFields?: (keyof Venue)[];
  setUpdated: Dispatch<SetStateAction<Venue | undefined>>;
}

const VenueDiffForm = ({
  updated,
  changedFields = [],
  setUpdated,
}: VenueDiffFormProps) => {
  const formFields = getVenueFormFields();

  return (
    <GenericDiffForm
      updated={updated}
      changedFields={changedFields}
      setUpdated={setUpdated}
      formFields={formFields}
    />
  );
};

export default VenueDiffForm;
