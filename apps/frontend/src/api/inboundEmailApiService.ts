import { ApplicationStatus } from "@/interfaces/entities/Application";
import { InboundEmail, InboundEmailState } from "@/interfaces/entities/InboundEmail";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { fetchRequest, sendRequest } from "./fetchHelper";

export const inboundEmailEndpoint = "/api/inbound-emails";

const getAll = (filters: { state?: InboundEmailState; application?: number } = {}) => {
  const params = new URLSearchParams({ limit: "100" });
  if (filters.state) params.set("state", filters.state);
  if (filters.application) params.set("application", filters.application.toString());
  return fetchRequest<PaginatedResponse<InboundEmail>>(
    `${inboundEmailEndpoint}?${params.toString()}`,
  );
};

const approve = (id: number, status?: ApplicationStatus): Promise<InboundEmail> => {
  return sendRequest<{ status?: ApplicationStatus }, InboundEmail>(
    `${inboundEmailEndpoint}/${id}/approve`,
    status ? { status } : {},
    "POST",
    "Application status updated",
  );
};

const get = (id: number): Promise<InboundEmail> => {
  return fetchRequest<InboundEmail>(`${inboundEmailEndpoint}/${id}`);
};

const link = (
  id: number,
  applicationId: number,
  options: { approve?: boolean; status?: ApplicationStatus } = {},
): Promise<InboundEmail> => {
  return sendRequest<
    { applicationId: number; approve?: boolean; status?: ApplicationStatus },
    InboundEmail
  >(
    `${inboundEmailEndpoint}/${id}/link`,
    { applicationId, ...options },
    "POST",
    options.approve ? "Application status updated" : "Email linked to application",
  );
};

const dismiss = (id: number): Promise<InboundEmail> => {
  return sendRequest<object, InboundEmail>(
    `${inboundEmailEndpoint}/${id}/dismiss`,
    {},
    "POST",
    "Reply dismissed",
  );
};

export const inboundEmailApiService = { getAll, get, approve, link, dismiss };
