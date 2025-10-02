import { AppDispatch } from "@/redux/store";
import { festivalApiService } from "@/api/festivalApiService";
import { setFestival, setSelectedFestival } from "@/redux/slices/festivalSlice";

export const refreshFestival = async (
  festivalId: number,
  dispatch: AppDispatch
) => {
  try {
    const newFestival = await festivalApiService.getFestival(festivalId);
    if (newFestival) {
      dispatch(setFestival(newFestival));
      dispatch(setSelectedFestival(newFestival));
    }
  } catch (error) {
    console.error("Failed to fetch festival:", error);
  }
};
