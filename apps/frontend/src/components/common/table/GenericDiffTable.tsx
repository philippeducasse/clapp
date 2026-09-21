import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { Dispatch, SetStateAction, ComponentType } from "react";

export interface GenericDiffTableProps<T> {
  original: T;
  updated: T;
  setUpdated: Dispatch<SetStateAction<T | undefined>>;
  formFields: ControlledFormElement[];
  DiffFormComponent: ComponentType<{
    updated: T;
    changedFields: (keyof T)[];
    setUpdated: Dispatch<SetStateAction<T | undefined>>;
  }>;
}

export const GenericDiffTable = <T extends Record<string, unknown>>({
  original,
  updated,
  setUpdated,
  formFields,
  DiffFormComponent,
}: GenericDiffTableProps<T>) => {
  const changedFields = formFields
    .map((f) => f.fieldName as keyof T)
    .filter((field) => original[field] !== updated[field]);

  return (
    <div className="flex">
      <div className="w-1/2">
        <Table className="table-fixed">
          <TableHeader>
            <TableRow>
              <TableHead className="w-1/3 text-xl text-primary">Field</TableHead>
              <TableHead className="w-2/3 text-xl text-primary">Original</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {formFields
              .filter((f) => !f.hidden)
              .map((field) => {
                const fieldName = field.fieldName as keyof T;
                const originalVal = original[fieldName] ?? "";
                const hasChanged = changedFields.includes(fieldName);

                return (
                  <TableRow key={String(fieldName)}>
                    <TableCell className="font-medium truncate">{field.label}</TableCell>
                    <TableCell
                      className={`truncate ${hasChanged ? "bg-red-50 dark:bg-red-950" : ""}`}
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
              <TableHead className="w-full text-xl text-primary">Updated</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <DiffFormComponent
              updated={updated}
              changedFields={changedFields}
              setUpdated={setUpdated}
            />
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
