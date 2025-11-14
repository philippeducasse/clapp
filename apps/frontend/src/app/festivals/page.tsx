import { festivalApiService } from "@/api/festivalApiService";
import { FestivalsTable } from "../../components/page-components/festivals/components/table/FestivalsTable";

const FestivalsPage = async () => {
  const festivals = await festivalApiService.getAll();

  return (
    <div className="container mx-auto py-10">
      <FestivalsTable initialData={festivals} />
    </div>
  );
};

export default FestivalsPage;
