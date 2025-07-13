import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Festival } from "@/interfaces/Festival";

interface DiffViewProps {
  original: Festival;
  updated: Festival;
}

export function FestivalDiffTable({ original, updated }: DiffViewProps) {
  const fields = Object.keys(original) as (keyof Festival)[];

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Field</TableHead>
          <TableHead>Original</TableHead>
          <TableHead>Updated</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {fields.map((field) => {
          const originalVal = original[field] ?? "";
          const updatedVal = updated[field] ?? "";
          const changed = originalVal !== updatedVal;

          return (
            <TableRow key={field}>
              <TableCell className="font-medium">{field}</TableCell>
              <TableCell>{String(originalVal)}</TableCell>
              <TableCell>{String(updatedVal)}</TableCell>
              <TableCell>
                {changed ? <Badge variant="destructive">Changed</Badge> : <Badge variant="outline">Unchanged</Badge>}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
