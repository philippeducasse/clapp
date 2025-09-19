import { Residency, ResidencyUpdate } from "@/interfaces/Residency";
import { get, post, put } from "./fetchHelper";
import { serialize } from "@/helpers/serializer";

const getResidencies = async (): Promise<Residency[]> => {
  return await get("/residencies");
};

const getResidency = async (id: number): Promise<Residency> => {
  return await get(`/residencies/${id}`);
};

const createResidency = async (
  residency: Partial<Residency>
): Promise<Residency> => {
  return await post("/residencies", residency);
};

const updateResidency = async (
  id: number,
  residency: Partial<Residency>
): Promise<Residency> => {
  return await put(`/residencies/${id}`, residency);
};

const getResidencyUpdates = async (): Promise<ResidencyUpdate[]> => {
  const residencies = await get("/residencies/updates");
  return serialize(residencies) as ResidencyUpdate[];
};

const refreshResidency = async (id: number): Promise<Residency> => {
  return await post(`/residencies/${id}/refresh`, {});
};

export const residencyApiService = {
  getResidencies,
  getResidency,
  createResidency,
  updateResidency,
  getResidencyUpdates,
  refreshResidency,
};
