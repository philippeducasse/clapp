import { transformKeysToCamelCase, transformKeysToSnakeCase } from "@/helpers/serializer";
import { toast } from "sonner";

export const fetchRequest = async <T = unknown>(url: string, options?: RequestInit): Promise<T> => {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    toast.error(`Error: ${text}`);
    throw new Error(`Failed to fetch ${url}: ${res.status}`);
  }
  const json = await res.json();
  return transformKeysToCamelCase(json);
};

export const sendRequest = async <TReq, TRes = TReq>(
  url: string,
  data: TReq,
  method: "POST" | "PUT" | "PATCH" = "POST",
  toastMessage?: string
): Promise<TRes> => {
  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(transformKeysToSnakeCase(data)),
  });

  if (!res.ok) {
    const error = await res.text();
    toast.error(`Error: ${error}`);
    throw new Error(`Failed to ${method} ${url}: ${res.status} - ${error}`);
  }

  const json = await res.json();

  toast.success(toastMessage ?? "Success");

  return json;

};

export const deleteRequest = async (url: string, toastMessage?: string): Promise<void> => {
  const res = await fetch(url, {
    method: "DELETE",
    headers: {
      Accept: "application/json",
    },
  });

  if (!res.ok) {
    const error = await res.text();
    toast.error(`Error: ${error}`);
    throw new Error(`Failed to DELETE ${url}: ${res.status} - ${error}`);
  }

  toast.success(toastMessage ?? "Successfully deleted");
};

export const sendFormDataRequest = async <TReq, TRes = TReq>(
  url: string,
  data: TReq,
  files?: File[],
  fileFieldName?: string,
  method: "POST" | "PUT" | "PATCH" = "POST",
  toastMessage?: string
): Promise<TRes> => {
  const formData = new FormData();

  const jsonData = transformKeysToSnakeCase(data);
  Object.keys(jsonData).forEach(key => {
    formData.append(key, jsonData[key]);
  });
  
  if(files && fileFieldName) {
    files.forEach(file => {
      formData.append(fileFieldName, file);
    });
  }

  const res = await fetch(url, {
    method,
    body: formData,
    headers: {
      Accept: "application/json",
    },
  });

  if (!res.ok) {
    const error = await res.text();
    toast.error(`Error: ${error}`);
    throw new Error(`Failed to ${method} ${url}: ${res.status} - ${error}`);
  }

  const json = await res.json();
  toast.success(toastMessage ?? "Success");
  return json;
};