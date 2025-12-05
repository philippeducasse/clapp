import { Suspense } from "react";
import { residencyApiService } from "@/api/residencyApiService";
import { ResidenciesTable } from "@/components/page-components/residencies/components/table/ResidenciesTable";
import TableSkeleton from "@/components/common/skeletons/TableSkeleton";

const ResidenciesPage = async () => {
  const data = await residencyApiService.getAll();
  return (
    <div className="container mx-auto py-10">
      <Suspense fallback={<TableSkeleton />}>
        <ResidenciesTable residencies={data.results} />
      </Suspense>
    </div>
  );
};

export default ResidenciesPage;
