import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Venue } from "@/interfaces/entities/Venue";
import VenueDiffForm from "../form/VenueDiffForm";
import { getVenueFormFields } from "../../helpers/getVenueFormFields";
import { Dispatch, SetStateAction } from "react";

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
  const changedFields = formFields
    .map((f) => f.fieldName)
    .filter(
      (field) =>
        original[field as keyof Venue] !== updated[field as keyof Venue]
    );

  return (
    <div className="flex">
      <div className="w-1/2">
        <Table className="table-fixed">
          <TableHeader>
            <TableRow>
              <TableHead className="w-1/3">Field</TableHead>
              <TableHead className="w-2/3">Original</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {formFields
              .filter((f) => !f.hidden)
              .map((field) => {
                const fieldName = field.fieldName as keyof Venue;
                const originalVal = original[fieldName] ?? "";
                const hasChanged = changedFields.includes(fieldName as string);

                return (
                  <TableRow key={fieldName}>
                    <TableCell className="font-medium truncate">
                      {field.label}
                    </TableCell>
                    <TableCell
                      className={`truncate ${
                        hasChanged ? "bg-red-50 dark:bg-red-950" : ""
                      }`}
                    >
                      {String(originalVal)}
                    </TableCell>
                  </TableRow>
                );
              })}
          </TableBody>
        </Table>
      </div>
      <div className="w-1/2">
        <Table className="table-fixed">
          <TableHeader>
            <TableRow>
              <TableHead className="w-full">Updated</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <VenueDiffForm
              updatedVenue={updated}
              changedFields={changedFields}
              setUpdated={setUpdated}
            />
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
