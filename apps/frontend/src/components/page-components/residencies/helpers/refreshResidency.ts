import { AppDispatch } from "@/redux/store";
import { setResidency } from "@/redux/slices/residencySlice";
import { residencyApiService } from "@/api/residencyApiService";

export const refreshResidency = async (
  residencyId: number,
  dispatch: AppDispatch
) => {
  const newResidency = await residencyApiService.getResidency(residencyId);
  dispatch(setResidency(newResidency));
};
