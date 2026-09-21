import { Dispatch, SetStateAction } from "react";
import { Residency } from "@/interfaces/entities/Residency";
import { getResidencyFormFields } from "../../helpers/form/getResidencyFormFields";
import GenericDiffForm from "@/components/common/form/GenericDiffForm";

interface ResidencyDiffFormProps {
  updated: Residency;
  changedFields?: (keyof Residency)[];
  setUpdated: Dispatch<SetStateAction<Residency | undefined>>;
}

const ResidencyDiffForm = ({
  updated,
  changedFields = [],
  setUpdated,
}: ResidencyDiffFormProps) => {
  const formFields = getResidencyFormFields();

  return (
    <GenericDiffForm
      updated={updated}
      changedFields={changedFields}
      setUpdated={setUpdated}
      formFields={formFields}
    />
  );
};

export default ResidencyDiffForm;
