import { venueApiService } from "../../../api/venueApiService";
import { VenuesTable } from "@/components/page-components/venues/components/table/VenuesTable";

const VenuesPage = async () => {
  const data = await venueApiService.getAll();
  return (
    <div className="container mx-auto py-10">
      <VenuesTable initialData={data} />
    </div>
  );
};

export default VenuesPage;
