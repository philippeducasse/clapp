import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Festival } from "@/interfaces/Festival";
import { DiffViewProps } from "@/interfaces/DiffViewProps";

export const FestivalDiffTable = ({ original, updated }: DiffViewProps) => {
  const fields = Object.keys(original) as (keyof Festival)[];

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Field</TableHead>
          <TableHead>Original</TableHead>
          <TableHead>Updated</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {fields.map((field) => {
          const originalVal = original[field] ?? "";
          const updatedVal = updated[field] ?? "";
          const changed = originalVal !== updatedVal;

          return (
            <TableRow key={field}>
              <TableCell className="font-medium max-w-sm">{field}</TableCell>
              <TableCell className={`max-w-sm ${changed ? "bg-red-100" : ""}`}> {String(originalVal)}</TableCell>
              <TableCell className={`max-w-sm ${changed ? "bg-green-50" : ""}`}>{String(updatedVal)}</TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
};
