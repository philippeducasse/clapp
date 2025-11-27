import { Profile } from "@/interfaces/entities/Profile";
import { fetchRequest, sendRequest, deleteRequest } from "./fetchHelper";
import { Credentials } from "@/interfaces/api/ApiService";

const endpoint = "/api/profiles";

const getProfile = async (): Promise<Profile> => {
  return await fetchRequest(`${endpoint}/me/`, { credentials: "include" });
};

const createProfile = async (profile: Partial<Profile>): Promise<Profile> => {
  return await sendRequest(`${endpoint}`, profile);
};

const deleteProfile = (profileId: number) => {
  return deleteRequest(`${endpoint}${profileId}`, "Profile successfully deleted");
};

const updateProfile = async (id: number, profile: Partial<Profile>): Promise<Profile> => {
  return await sendRequest(
    `${endpoint}/${id}`,
    profile,
    "PUT",
    "Profile successfully updated",
    true
  );
};

const login = async (credentials: Credentials) => {
  return await sendRequest(
    `${endpoint}/login`,
    credentials,
    "POST",
    `Welcome ${credentials.email}, you have successfully logged in`,
    true
  );
};

export const profileApiService = {
  getProfile,
  createProfile,
  updateProfile,
  deleteProfile,
  login,
};
