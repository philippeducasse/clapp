import { Festival } from "@/interfaces/entities/Festival";
import FestivalDiffForm from "@/components/page-components/festivals/components/form/FestivalDiffForm";
import { getFestivalFormFields } from "../../helpers/form/getFestivalFormFields";
import { Dispatch, SetStateAction } from "react";
import { GenericDiffTable } from "@/components/common/table/GenericDiffTable";

export interface DiffViewProps {
  original: Festival;
  updated: Festival;
  setUpdated: Dispatch<SetStateAction<Festival | undefined>>;
}

export const FestivalDiffTable = ({
  original,
  updated,
  setUpdated,
}: DiffViewProps) => {
  const formFields = getFestivalFormFields(true);

  return (
    <GenericDiffTable
      original={original}
      updated={updated}
      setUpdated={setUpdated}
      formFields={formFields}
      DiffFormComponent={FestivalDiffForm}
    />
  );
};
