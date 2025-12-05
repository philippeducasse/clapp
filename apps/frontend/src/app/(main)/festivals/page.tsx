import { Suspense } from "react";
import { festivalApiService } from "@/api/festivalApiService";
import { FestivalsTable } from "../../../components/page-components/festivals/components/table/FestivalsTable";
import TableSkeleton from "@/components/common/skeletons/TableSkeleton";

const FestivalsPage = async () => {
  const festivals = await festivalApiService.getAll();

  return (
    <div className="container mx-auto py-10">
      <Suspense fallback={<TableSkeleton />}>
        <FestivalsTable initialData={festivals} />
      </Suspense>
    </div>
  );
};

export default FestivalsPage;
