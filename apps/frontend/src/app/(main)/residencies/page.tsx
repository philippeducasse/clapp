import { residencyApiService } from "@/api/residencyApiService";
import { ResidenciesTable } from "@/components/page-components/residencies/components/table/ResidenciesTable";

export const dynamic = "force-dynamic";

const ResidenciesPage = async () => {
  const data = await residencyApiService.getAll();
  return (
    <div className="container mx-auto py-10">
      <ResidenciesTable initialData={data} />
    </div>
  );
};

export default ResidenciesPage;
