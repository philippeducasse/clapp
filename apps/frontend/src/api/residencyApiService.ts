import { Residency } from "@/interfaces/entities/Residency";
import { fetchRequest, sendRequest, deleteRequest } from "./fetchHelper";
import { PaginatedResponse } from "@/interfaces/PaginatedResponse";
import { EntityApiService } from "@/interfaces/api/ApiService";

const endpoint = "http://localhost:8000/api/residencies/";

const getResidencies = async (): Promise<PaginatedResponse<Residency>> => {
  return await fetchRequest<PaginatedResponse<Residency>>(endpoint);
};

const getResidency = async (id: number): Promise<Residency> => {
  return await fetchRequest(`${endpoint}${id}/`);
};

const createResidency = async (
  residency: Residency
): Promise<Residency> => {
  return await sendRequest(`${endpoint}`, residency);
};

const deleteResidency = (residencyId: number): Promise<void> => {
  return deleteRequest(
    `${endpoint}${residencyId}`,
    "Residency successfully deleted"
  );
};

const updateResidency = async (
  residency: Residency
): Promise<Residency> => {
  return await sendRequest(`${endpoint}/${residency.id}`, residency);
};

const enrichResidency = async (id: number): Promise<Residency> => {
  return fetchRequest(`${endpoint}${id}/enrich/`);
};

const generateEmail = (residencyId: number): Promise<{ message: string }> => {
  return sendRequest<{ message: string }>(
    `${endpoint}${residencyId}/generate_email/`,
    { message: "" },
    "POST",
    "Email successfully generated"
  );
};

export const residencyApiService: EntityApiService<Residency> & {
  getResidencies: typeof getResidencies;
  getResidency: typeof getResidency;
  createResidency: typeof createResidency;
  updateResidency: typeof updateResidency;
  deleteResidency: typeof deleteResidency;
  enrichResidency: typeof enrichResidency;
  generateEmail: typeof generateEmail;
} = {
  // Interface methods
  getAll: getResidencies,
  get: getResidency,
  create: createResidency,
  update: updateResidency,
  delete: deleteResidency,
  enrich: enrichResidency,
  // Legacy method names for backwards compatibility
  getResidencies,
  getResidency,
  createResidency,
  updateResidency,
  deleteResidency,
  enrichResidency,
  // Entity-specific methods
  generateEmail,
};
