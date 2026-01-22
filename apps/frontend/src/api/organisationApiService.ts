import { fetchRequest, sendFormDataRequest } from "./fetchHelper";

const endpoint = "/api/organisations";

export interface OrganisationSearchResponse {
  id: number;
  name: string;
  country: string;
  town: string;
  type: string;
}

const search = async (
  searchQuery: string,
  type?: string,
): Promise<OrganisationSearchResponse[]> => {
  if (!searchQuery || searchQuery.length < 2) {
    return [];
  }
  const typeParam = type ? `&type=${type.toLowerCase()}` : "";
  return await fetchRequest(`${endpoint}/search/?q=${searchQuery}${typeParam}`);
};
const upload = async (excelFile: File[]) => {
  return await sendFormDataRequest(`${endpoint}/upload/`, undefined, excelFile, "excel", "POST");
};

export const organisationApiService = {
  search,
  upload,
};
