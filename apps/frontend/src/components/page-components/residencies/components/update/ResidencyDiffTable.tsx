import { Residency } from "@/interfaces/entities/Residency";
import ResidencyDiffForm from "../form/ResidencyDiffForm";
import { getResidencyFormFields } from "../../helpers/form/getResidencyFormFields";
import { Dispatch, SetStateAction } from "react";
import { GenericDiffTable } from "@/components/common/table/GenericDiffTable";

export interface DiffViewProps {
  original: Residency;
  updated: Residency;
  setUpdated: Dispatch<SetStateAction<Residency | undefined>>;
}

export const ResidencyDiffTable = ({
  original,
  updated,
  setUpdated,
}: DiffViewProps) => {
  const formFields = getResidencyFormFields();

  return (
    <GenericDiffTable
      original={original}
      updated={updated}
      setUpdated={setUpdated}
      formFields={formFields}
      DiffFormComponent={ResidencyDiffForm}
    />
  );
};
