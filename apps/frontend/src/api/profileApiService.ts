import { Profile } from "@/interfaces/entities/Profile";
import { fetchRequest, sendRequest, deleteRequest } from "./fetchHelper";
import { Credentials } from "@/interfaces/api/ApiService";
const endpoint = "/api/profiles";

const get = async (): Promise<Profile> => {
  return await fetchRequest(`${endpoint}/me/`, { credentials: "include" });
};

const register = async (profile: Partial<Profile>): Promise<Profile> => {
  return await sendRequest(
    `${endpoint}/register`,
    profile,
    "POST",
    "Profile successfully created!"
  );
};

const remove = (profileId: number) => {
  return deleteRequest(`${endpoint}${profileId}`, "Profile successfully deleted");
};

const update = async (profile: Partial<Profile>): Promise<Profile> => {
  return await sendRequest(
    `${endpoint}/${profile.id}`,
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
const logout = async () => {
  return await sendRequest(`${endpoint}/logout`, {}, "POST", `Successfully logged out`, true);
};

export const profileApiService = {
  get,
  register,
  update,
  remove,
  login,
  logout,
};
