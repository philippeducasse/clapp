import festivalApiService from "@/api/festivalApiService";
import { FestivalsTable } from "../../components/page-components/festivals/components/table/FestivalsTable";

const FestivalsPage = async () => {
  const data = await festivalApiService.getAllFestivals();
  return (
    <div className="container mx-auto py-10">
      <FestivalsTable festivals={data} />
    </div>
  );
};

export default FestivalsPage;
