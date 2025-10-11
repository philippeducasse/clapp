import { festivalApiService } from "@/api/festivalApiService";
import { FestivalsTable } from "../../components/page-components/festivals/components/table/FestivalsTable";

const FestivalsPage = async () => {
  const festivals = await festivalApiService.getAllFestivals(50, 0);

  return (
    <div className="container mx-auto py-10">
      <FestivalsTable initialData={festivals} />
    </div>
  );
};

export default FestivalsPage;
