import { festivalApiService } from "@/api/festivalApiService";
import { FestivalsTable } from "../../../components/page-components/festivals/components/table/FestivalsTable";
import { getDefaultFilters, toFilterParams } from "@/helpers/defaultFilters";
import { EntityName } from "@/interfaces/Enums";

export const dynamic = "force-dynamic";

const FestivalsPage = async () => {
  // Apply default filters server-side so the first render is already filtered.
  const initialColumnFilters = getDefaultFilters(EntityName.FESTIVAL, null);
  const festivals = await festivalApiService.getAll({
    filters: toFilterParams(initialColumnFilters),
  });

  return (
    <div className="container mx-auto py-10">
      <FestivalsTable initialData={festivals} initialColumnFilters={initialColumnFilters} />
    </div>
  );
};

export default FestivalsPage;
