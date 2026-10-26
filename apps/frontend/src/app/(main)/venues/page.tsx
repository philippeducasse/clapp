import { venueApiService } from "../../../api/venueApiService";
import { VenuesTable } from "@/components/page-components/venues/components/table/VenuesTable";
import { getDefaultFilters, toFilterParams } from "@/helpers/defaultFilters";
import { EntityName } from "@/interfaces/Enums";

export const dynamic = "force-dynamic";

const VenuesPage = async () => {
  // Apply default filters server-side so the first render is already filtered.
  const initialColumnFilters = getDefaultFilters(EntityName.VENUE, null);
  const data = await venueApiService.getAll({
    filters: toFilterParams(initialColumnFilters),
  });
  return (
    <div className="container mx-auto py-10">
      <VenuesTable initialData={data} initialColumnFilters={initialColumnFilters} />
    </div>
  );
};

export default VenuesPage;
