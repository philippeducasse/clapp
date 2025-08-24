import festivalApiService from "@/api/festivalApiService";
import { FestivalTable } from "../../components/page-components/festivals/components/view/FestivalTable";

const FestivalsPage = async () => {
  const data = await festivalApiService.getAllFestivals();
  return (
    <div className="container mx-auto py-10">
      <FestivalTable festivals={data} />
    </div>
  );
};

export default FestivalsPage;
