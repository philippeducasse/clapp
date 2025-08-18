import festivalApiService from "@/api/festivalApiService";
import { FestivalTable } from "../../components/page-components/festival-page/components/View/FestivalTable";

const FestivalsPage = async () => {
  const data = await festivalApiService.getAllFestivals();
  return (
    <div className="container mx-auto py-10">
      <FestivalTable data={data} />
    </div>
  );
};

export default FestivalsPage;
