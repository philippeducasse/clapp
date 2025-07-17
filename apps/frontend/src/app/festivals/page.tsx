import festivalApiService from "@/api/festivalApiService";
import { FestivalTable } from "./components/festival-table";

export default async function FestivalsPage() {
  const data = await festivalApiService.getAllFestivals();
  return (
    <div className="container mx-auto py-10">
      <FestivalTable data={data} />
    </div>
  );
}
