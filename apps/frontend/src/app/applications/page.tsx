import { applicationApiService } from "@/api/applicationApiService";
import { ApplicationsTable } from "@/components/page-components/applications/table/ApplicationsTable";
const ApplicationsPage = async () => {
  const data = await applicationApiService.getAllApplications();
  console.log("data:", data)
  return (
    <div className="container mx-auto py-10">
      <ApplicationsTable initialData={data} />
    </div>
  );
};

export default ApplicationsPage;
