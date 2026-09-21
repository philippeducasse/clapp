import { ResidencyDiffTable } from "./ResidencyDiffTable";
import { Residency } from "@/interfaces/entities/Residency";
import { residencyApiService } from "@/api/residencyApiService";
import { useDispatch, useSelector } from "react-redux";
import { selectResidency, updateResidency } from "@/redux/slices/residencySlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { UpdateDialog } from "@/components/common/modals/UpdateDialog";

export const ResidencyUpdateDialog = () => {
  const dispatch = useDispatch();
  const params = useParams();
  const residencyId = Number(params.id);
  const residency = useSelector((state: RootState) => selectResidency(state, residencyId));

  return (
    <UpdateDialog<Residency>
      entity={residency}
      entityName="Residency"
      DiffTableComponent={ResidencyDiffTable}
      onEnrich={() => residencyApiService.enrich(residency!.id)}
      onUpdate={async (updated) => {
        await residencyApiService.update(updated);
        dispatch(updateResidency(updated));
      }}
    />
  );
};
