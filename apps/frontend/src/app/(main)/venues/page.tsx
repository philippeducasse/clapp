import { Suspense } from "react";
import { venueApiService } from "../../../api/venueApiService";
import { VenuesTable } from "@/components/page-components/venues/components/table/VenuesTable";
import TableSkeleton from "@/components/common/skeletons/TableSkeleton";

const VenuesPage = async () => {
  const data = await venueApiService.getAll();
  return (
    <div className="container mx-auto py-10">
      <Suspense fallback={<TableSkeleton />}>
        <VenuesTable venues={data.results} />
      </Suspense>
    </div>
  );
};

export default VenuesPage;
