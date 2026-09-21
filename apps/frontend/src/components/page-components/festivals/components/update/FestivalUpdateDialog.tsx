import { FestivalDiffTable } from "./FestivalDiffTable";
import { Festival } from "@/interfaces/entities/Festival";
import { festivalApiService } from "@/api/festivalApiService";
import { useDispatch, useSelector } from "react-redux";
import { selectFestival, updateFestival } from "@/redux/slices/festivalSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { UpdateDialog } from "@/components/common/modals/UpdateDialog";

export const FestivalUpdateDialog = () => {
  const dispatch = useDispatch();
  const params = useParams();
  const festivalId = Number(params.id);
  const festival = useSelector((state: RootState) => selectFestival(state, festivalId));

  return (
    <UpdateDialog<Festival>
      entity={festival}
      entityName="Festival"
      DiffTableComponent={FestivalDiffTable}
      onEnrich={() => festivalApiService.enrich(festival!.id)}
      onUpdate={async (updated) => {
        await festivalApiService.update(updated);
        dispatch(updateFestival(updated));
      }}
    />
  );
};
