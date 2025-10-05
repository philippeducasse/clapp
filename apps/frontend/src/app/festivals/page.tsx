import { festivalApiService } from "@/api/festivalApiService";
import { FestivalsTable } from "../../components/page-components/festivals/components/table/FestivalsTable";

const FestivalsPage = async () => {
  const festivals = await festivalApiService.getAllFestivals();
  // const applications = await applicationsApiService.getAllApplications();

  return (
    <div className="container mx-auto py-10">
      <FestivalsTable festivals={festivals} />
    </div>
  );
};

export default FestivalsPage;
