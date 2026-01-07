import { Dispatch, SetStateAction } from "react";
import { Festival } from "@/interfaces/entities/Festival";
import { getFestivalFormFields } from "../../helpers/form/getFestivalFormFields";
import GenericDiffForm from "@/components/common/form/GenericDiffForm";

interface FestivalDiffFormProps {
  updated: Festival;
  changedFields?: (keyof Festival)[];
  setUpdated: Dispatch<SetStateAction<Festival | undefined>>;
}

const FestivalDiffForm = ({
  updated,
  changedFields = [],
  setUpdated,
}: FestivalDiffFormProps) => {
  const formFields = getFestivalFormFields(true);

  return (
    <GenericDiffForm
      updated={updated}
      changedFields={changedFields}
      setUpdated={setUpdated}
      formFields={formFields}
    />
  );
};

export default FestivalDiffForm;
