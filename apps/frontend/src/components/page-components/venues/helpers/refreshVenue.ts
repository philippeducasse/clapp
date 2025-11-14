import { AppDispatch } from "@/redux/store";
import { venueApiService } from "@/api/venueApiService";
import { setVenue } from "@/redux/slices/venueSlice";

export const refreshVenue = async (venueId: number, dispatch: AppDispatch) => {
  try {
    const newVenue = await venueApiService.get(venueId);
    if (newVenue) {
      dispatch(setVenue(newVenue));
    }
  } catch (error) {
    console.error("Failed to fetch venue:", error);
  }
};
