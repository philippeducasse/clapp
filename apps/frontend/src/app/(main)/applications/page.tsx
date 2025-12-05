import { Suspense } from "react";
import { applicationApiService } from "@/api/applicationApiService";
import { ApplicationsTable } from "@/components/page-components/applications/components/table/ApplicationsTable";
import TableSkeleton from "@/components/common/skeletons/TableSkeleton";

const ApplicationsPage = async () => {
  const data = await applicationApiService.getAllApplications();
  return (
    <div className="container mx-auto py-10">
      <Suspense fallback={<TableSkeleton />}>
        <ApplicationsTable initialData={data} />
      </Suspense>
    </div>
  );
};

export default ApplicationsPage;
