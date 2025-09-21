import { residencyApiService } from "@/api/residencyApiService";
import { ResidenciesTable } from "@/components/page-components/residencies/components/table/ResidenciesTable";

const ResidenciesPage = async () => {
  const data = await residencyApiService.getResidencies();
  return (
    <div className="container mx-auto py-10">
      <ResidenciesTable residencies={data} />;
    </div>
  );
};

export default ResidenciesPage;
