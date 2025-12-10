import { fetchRequest } from "./fetchHelper";

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
  type?: string
): Promise<OrganisationSearchResponse[]> => {
  if (!searchQuery || searchQuery.length < 2) {
    return [];
  }
  const typeParam = type ? `&type=${type.toLowerCase()}` : "";
  return await fetchRequest(`${endpoint}/search/?q=${searchQuery}${typeParam}`);
};

export const organisationApiService = {
  search,
};
