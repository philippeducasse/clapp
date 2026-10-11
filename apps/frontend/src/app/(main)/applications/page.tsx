import { applicationApiService } from "@/api/applicationApiService";
import { profileApiService } from "@/api/profileApiService";
import { ApplicationsTable } from "@/components/page-components/applications/components/table/ApplicationsTable";
import { getDefaultFilters, toFilterParams } from "@/helpers/defaultFilters";
import { EntityName } from "@/interfaces/Enums";

export const dynamic = "force-dynamic";

const ApplicationsPage = async () => {
  // Apply default filters server-side so the first render is already filtered.
  const profile = await profileApiService.get().catch(() => null);
  const initialColumnFilters = getDefaultFilters(EntityName.APPLICATION, profile);

  const data = await applicationApiService.getAll({
    filters: toFilterParams(initialColumnFilters),
  });

  return (
    <div className="container mx-auto py-10">
      <ApplicationsTable initialData={data} initialColumnFilters={initialColumnFilters} />
    </div>
  );
};

export default ApplicationsPage;
