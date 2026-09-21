import { applicationApiService } from "@/api/applicationApiService";
import { ApplicationsTable } from "@/components/page-components/applications/components/table/ApplicationsTable";

export const dynamic = "force-dynamic";

const ApplicationsPage = async () => {
  const data = await applicationApiService.getAll();
  return (
    <div className="container mx-auto py-10">
      <ApplicationsTable initialData={data} />
    </div>
  );
};

export default ApplicationsPage;
