import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Festival } from "@/interfaces/Festival";
import { DiffViewProps } from "@/interfaces/DiffViewProps";
import FestivalDiffForm from "@/components/page-components/festivals/components/form/FestivalDiffForm";
import { getFestivalFormFields } from "../../helpers/getFestivalFormFields";

export const FestivalDiffTable = ({ original, updated, setUpdated }: DiffViewProps) => {
  const formFields = getFestivalFormFields();
  const changedFields = formFields
    .map((f) => f.fieldName)
    .filter((field) => original[field as keyof Festival] !== updated[field as keyof Festival]);

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
                const fieldName = field.fieldName as keyof Festival;
                const originalVal = original[fieldName] ?? "";
                const hasChanged = changedFields.includes(fieldName as string);

                return (
                  <TableRow key={fieldName}>
                    <TableCell className="font-medium truncate">{field.label}</TableCell>
                    <TableCell className={`truncate ${hasChanged ? "bg-red-50 dark:bg-red-950" : ""}`}>
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
            <FestivalDiffForm updatedFestival={updated} changedFields={changedFields} setUpdated={setUpdated} />
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
