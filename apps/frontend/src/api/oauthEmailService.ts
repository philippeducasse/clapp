import { fetchRequest, sendRequest } from "./fetchHelper";

const endpoint = "/api/profiles/oauth";

interface OAuthConnectResponse {
  authUrl: string;
}

const connectGmail = async (): Promise<void> => {
  const response = await fetchRequest<OAuthConnectResponse>(`${endpoint}/gmail/connect/`);
  window.location.href = response.authUrl;
};

const connectOutlook = async (): Promise<void> => {
  const response = await fetchRequest<OAuthConnectResponse>(`${endpoint}/outlook/connect/`);
  console.log({ response });
  window.location.href = response.authUrl;
};

const disconnect = async (): Promise<void> => {
  await sendRequest(`${endpoint}/disconnect/`, {}, "POST", "OAuth connection removed");
};

export const oauthEmailService = {
  connectGmail,
  connectOutlook,
  disconnect,
};
