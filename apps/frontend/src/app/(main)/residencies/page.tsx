import { residencyApiService } from "@/api/residencyApiService";
import { ResidenciesTable } from "@/components/page-components/residencies/components/table/ResidenciesTable";
import { getDefaultFilters, toFilterParams } from "@/helpers/defaultFilters";
import { EntityName } from "@/interfaces/Enums";

export const dynamic = "force-dynamic";

const ResidenciesPage = async () => {
  // Apply default filters server-side so the first render is already filtered.
  const initialColumnFilters = getDefaultFilters(EntityName.RESIDENCY, null);
  const data = await residencyApiService.getAll({
    filters: toFilterParams(initialColumnFilters),
  });
  return (
    <div className="container mx-auto py-10">
      <ResidenciesTable initialData={data} initialColumnFilters={initialColumnFilters} />
    </div>
  );
};

export default ResidenciesPage;
