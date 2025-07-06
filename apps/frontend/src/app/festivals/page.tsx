"use client";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import useFestivals from "@/hooks/useFestivals";

const festivalTable = () => {
  const festivals = useFestivals();
  console.log("festivals:", festivals);

  return (
    <Table>
      <TableCaption>Festivals</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[100px]">Name</TableHead>
          <TableHead>Country</TableHead>
          <TableHead>Website</TableHead>
          <TableHead className="text-right">Amount</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {festivals?.map((f) => (
          <TableRow key={f.id}>
            <TableCell className="font-medium">{f.festivalName}</TableCell>
            <TableCell>{f.country}</TableCell>
            <TableCell>{f.websiteUrl}</TableCell>
            <TableCell className="text-right">{f.dateString}</TableCell>
          </TableRow>
        ))}
      </TableBody>
      <TableFooter>
        <TableRow>
          <TableCell colSpan={3}>Total</TableCell>
          <TableCell className="text-right">{festivals.length}</TableCell>
        </TableRow>
      </TableFooter>
    </Table>
  );
};

export default festivalTable;
