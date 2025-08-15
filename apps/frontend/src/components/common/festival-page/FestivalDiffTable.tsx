import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Festival } from "@/interfaces/Festival";
import { DiffViewProps } from "@/interfaces/DiffViewProps";
import FestivalDiffForm from "@/app/festivals/components/FestivalDiffForm";

export const FestivalDiffTable = ({ original, updated }: DiffViewProps) => {
  const { id: _, ...originalWithoutId } = original;

  const fields = Object.keys(originalWithoutId) as (keyof Festival)[];
  return (
    <div className="flex ">
      <Table className="table-fixed" tableWidth={"w-1/2"}>
        <TableHeader>
          <TableRow>
            <TableHead className="w-1/2">Field</TableHead>
            <TableHead className="w-1/2">Original</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {fields.map((field) => {
            const originalVal = originalWithoutId[field] ?? "";
            const updatedVal = updated[field] ?? "";
            const changed = originalVal !== updatedVal;

            return (
              <TableRow key={field}>
                <TableCell className="font-medium truncate">{field}</TableCell>
                <TableCell className={`truncate ${changed ? "bg-red-100" : ""}`}> {String(originalVal)}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      <div className="w-full">
        <p className="text-foreground h-10 px-2 text-left align-middle font-medium whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]">
          Updated
        </p>
        <FestivalDiffForm updatedFestival={updated} />
      </div>
    </div>
  );
};
