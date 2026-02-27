import { Profile } from "@/interfaces/entities/Profile";
import { fetchRequest, sendRequest, deleteRequest } from "./fetchHelper";
import { Credentials } from "@/interfaces/api/ApiService";

const endpoint = "/api/profiles";

const get = async (): Promise<Profile> => {
  return await fetchRequest(`${endpoint}/me`);
};

const register = async (profile: Partial<Profile>): Promise<Profile> => {
  return await sendRequest(
    `${endpoint}/register`,
    profile,
    "POST",
    "Profile successfully created!",
  );
};

const remove = (profileId: number) => {
  return deleteRequest(`${endpoint}/${profileId}`, "Profile successfully deleted", true);
};

const update = async (profile: Partial<Profile>): Promise<Profile> => {
  return await sendRequest(
    `${endpoint}/${profile.id}`,
    profile,
    "PUT",
    "Profile successfully updated",
    true,
  );
};

const login = async (credentials: Credentials): Promise<Profile> => {
  return await sendRequest<Credentials, Profile>(
    `${endpoint}/login`,
    credentials,
    "POST",
    `Welcome ${credentials.email}, you have successfully logged in`,
    true,
  );
};

const logout = async () => {
  return await sendRequest(`${endpoint}/logout`, {}, "POST", `Successfully logged out`, true);
};

const changePassword = async (newPassword: Record<string, unknown>, isReset: boolean) => {
  const passwordEndPoint = isReset ? "reset-password" : "change_password";

  return await sendRequest(
    `${endpoint}/${passwordEndPoint}`,
    newPassword,
    "POST",
    `Password successfully changed`,
    true,
  );
};

const forgotPassword = async (email: Record<string, unknown>) => {
  return await sendRequest(
    `${endpoint}/forgot-password`,
    email,
    "POST",
    `Your request has been sent, please check your email ${email.email}`,
    true,
  );
};

export const profileApiService = {
  get,
  register,
  update,
  remove,
  login,
  logout,
  changePassword,
  forgotPassword,
};
