import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Festival } from "@/interfaces/Festival";
import { DiffViewProps } from "@/interfaces/DiffViewProps";
import FestivalDiffForm from "@/app/festivals/components/FestivalDiffForm";

export const FestivalDiffTable = ({ original, updated }: DiffViewProps) => {
  const fields = Object.keys(original) as (keyof Festival)[];

  return (
    <div className="flex ">
      <Table className="">
        <TableHeader>
          <TableRow>
            <TableHead>Field</TableHead>
            <TableHead>Original</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {fields.map((field) => {
            const originalVal = original[field] ?? "";
            const updatedVal = updated[field] ?? "";
            const changed = originalVal !== updatedVal;

            return (
              <TableRow key={field}>
                <TableCell className="font-medium max-w-xs">{field}</TableCell>
                <TableCell className={`max-w-sm ${changed ? "bg-red-100" : ""}`}> {String(originalVal)}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      <div className="">
        <p className="text-foreground h-10 px-2 text-left align-middle font-medium whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]">
          Updated
        </p>
        <FestivalDiffForm updatedFestival={updated} />
      </div>
    </div>
  );
};
