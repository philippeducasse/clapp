import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Festival } from "@/interfaces/Festival";
import { DiffViewProps } from "@/interfaces/DiffViewProps";
import FestivalDiffForm from "@/components/page-components/festival-page/components/form/FestivalDiffForm";
import { startCase } from "lodash";

export const FestivalDiffTable = ({ original, updated }: DiffViewProps) => {
  // eslint-disable-next-line  @typescript-eslint/no-unused-vars
  const { id: _, ...originalWithoutId } = original;

  const fields = Object.keys(originalWithoutId) as (keyof Festival)[];
  const changedFields = fields.filter((field) => originalWithoutId[field] !== updated[field]);
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
          {fields
            .filter((field) => field !== "description")
            .map((field) => {
              const originalVal = originalWithoutId[field] ?? "";
              const updatedVal = updated[field] ?? "";
              const changed = originalVal !== updatedVal;
              return (
                <TableRow key={String(field)}>
                  <TableCell className="font-medium truncate">{startCase(String(field))}</TableCell>
                  <TableCell className={`truncate ${changed ? "bg-red-50" : ""}`}>{String(originalVal)}</TableCell>
                </TableRow>
              );
            })}

          {fields.includes("description") && (
            <TableRow key="description">
              <TableCell className="font-medium truncate">{startCase("description")}</TableCell>
              <TableCell
                className={`truncate ${originalWithoutId.description !== updated.description ? "bg-red-50" : ""}`}
              >
                {String(originalWithoutId.description ?? "")}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
      <div className="w-full">
        <p className="pt-2 text-base font-normal hover:bg-muted/50 data-[state=selected]:bg-muted border-b transition-colors text-foreground h-10 px-2 text-left align-middle font-medium whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]">
          Updated
        </p>
        <FestivalDiffForm updatedFestival={updated} changedFields={changedFields} />
      </div>
    </div>
  );
};
