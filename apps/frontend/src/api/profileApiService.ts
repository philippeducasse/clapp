import { Profile } from "@/interfaces/entities/Profile";
import { fetchRequest, sendRequest, deleteRequest } from "./fetchHelper";

const endpoint = "http://localhost:8000/api/profiles";

const getProfile = async (): Promise<Profile> => {
  return await fetchRequest(`${endpoint}/me/`);
};

const createProfile = async (profile: Partial<Profile>): Promise<Profile> => {
  return await sendRequest(`${endpoint}`, profile);
};

const deleteProfile = (profileId: number) => {
  return deleteRequest(
    `${endpoint}${profileId}`,
    "Profile successfully deleted"
  );
};

const updateProfile = async (
  id: number,
  profile: Partial<Profile>
): Promise<Profile> => {
  return await sendRequest(`${endpoint}/${id}`, profile);
};

export const profileApiService = {
  getProfile,
  createProfile,
  updateProfile,
  deleteProfile,
};
