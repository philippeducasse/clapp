import { Festival } from "@/interfaces/festival";
import { columns } from "./columns";
import { DataTable } from "@/components/ui/data-table";
import camelcaseKeys from "camelcase-keys";
import festivalApiService from "@/api/festivalApiService";

export default async function FestivalsPage() {
  const data = await festivalApiService.getAllFestivals();

  return (
    <div className="container mx-auto py-10">
      <DataTable columns={columns} data={data} />
    </div>
  );
}
