import { Festival } from "@/interfaces/festival";
import { columns } from "./columns";
import { DataTable } from "@/components/ui/data-table";
import camelcaseKeys from "camelcase-keys";

async function fetchFestivals(): Promise<Festival[]> {
  let festivals = [];
  try {
    const data = await fetch("http://localhost:8000/api/festivals/");
    const json = await data.json();
    festivals = camelcaseKeys(json, { deep: true });
  } catch (error) {
    console.error(`Error fetching festivals: ${error}`);
  }
  return festivals;
}

export default async function FestivalsPage() {
  console.log("cols: ", columns);
  const data = await fetchFestivals();

  return (
    <div className="container mx-auto py-10">
      <DataTable columns={columns} data={data} />
    </div>
  );
}
