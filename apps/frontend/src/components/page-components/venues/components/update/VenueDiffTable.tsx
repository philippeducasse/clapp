import { Venue } from "@/interfaces/entities/Venue";
import VenueDiffForm from "../form/VenueDiffForm";
import { getVenueFormFields } from "../../helpers/form/getVenueFormFields";
import { Dispatch, SetStateAction } from "react";
import { GenericDiffTable } from "@/components/common/table/GenericDiffTable";

export interface DiffViewProps {
  original: Venue;
  updated: Venue;
  setUpdated: Dispatch<SetStateAction<Venue | undefined>>;
}

export const VenueDiffTable = ({
  original,
  updated,
  setUpdated,
}: DiffViewProps) => {
  const formFields = getVenueFormFields();

  return (
    <GenericDiffTable
      original={original}
      updated={updated}
      setUpdated={setUpdated}
      formFields={formFields}
      DiffFormComponent={VenueDiffForm}
    />
  );
};
