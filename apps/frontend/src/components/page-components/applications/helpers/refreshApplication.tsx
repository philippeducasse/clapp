import { AppDispatch } from "@/redux/store";
import { applicationApiService } from "@/api/applicationApiService";
import { setApplication } from "@/redux/slices/applicationSlice";

export const refreshApplication = async (applicationId: number, dispatch: AppDispatch) => {
  try {
    const newApplication = await applicationApiService.getApplication(applicationId);
    if (newApplication) {
      dispatch(setApplication(newApplication));
    }
  } catch (error) {
    console.error("Failed to fetch application:", error);
  }
};
