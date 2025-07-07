import camelcaseKeys from "camelcase-keys";

export async function fetchJson<T = unknown>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  const json = await res.json();
  return camelcaseKeys(json, { deep: true });
}
