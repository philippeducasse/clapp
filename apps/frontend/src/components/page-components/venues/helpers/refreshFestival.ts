import { AppDispatch } from "@/redux/store";
import venueApiService from "@/api/venueApiService";
import { setVenue, setSelectedVenue } from "@/redux/slices/venueSlice";

export const refreshVenue = async (venueId: number, dispatch: AppDispatch) => {
  try {
    const newVenue = await venueApiService.getVenue(venueId);
    if (newVenue) {
      dispatch(setVenue(newVenue));
      dispatch(setSelectedVenue(newVenue));
    }
  } catch (error) {
    console.error("Failed to fetch venue:", error);
  }
};
