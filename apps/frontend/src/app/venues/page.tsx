import { venueApiService } from "../../api/venueApiService";
import { VenuesTable } from "@/components/page-components/venues/components/table/VenuesTable";

const VenuesPage = async () => {
  const data = await venueApiService.getAll();
  return (
    <div className="container mx-auto py-10">
      <VenuesTable venues={data.results} />
    </div>
  );
};

export default VenuesPage;
