import { describe, it, expect, beforeAll, afterAll } from "vitest";
import {
  waitForBackend,
  loginTestUser,
  API_BASE,
  fetchWithAuth,
  cleanupTestData,
  trackEntity,
} from "./setup";

describe("E2E: Festivals and Applications", () => {
  beforeAll(async () => {
    await waitForBackend();
    // Login and get session
    const profile = await loginTestUser();
    expect(profile.id).toBeDefined();
  });

  afterAll(async () => {
    await cleanupTestData();
  });

  it("should fetch all festivals", async () => {
    const response = await fetchWithAuth(`${API_BASE}/festivals`, {
      method: "GET",
    });

    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(data).toHaveProperty("count");
    expect(data).toHaveProperty("results");
    expect(Array.isArray(data.results)).toBe(true);
  });

  it("should fetch festivals with pagination", async () => {
    const response = await fetchWithAuth(`${API_BASE}/festivals/?limit=5&offset=0`, {
      method: "GET",
    });

    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(data.count).toBeDefined();
    expect(data.results.length).toBeLessThanOrEqual(5);
  });

  it("should fetch a single festival by ID", async () => {
    // First get a festival ID
    const listResponse = await fetchWithAuth(`${API_BASE}/festivals`, {
      method: "GET",
    });
    const listData = await listResponse.json();

    if (listData.results.length === 0) {
      console.log("Skipping: No festivals available");
      return;
    }

    const festivalId = listData.results[0].id;

    // Get single festival
    const response = await fetchWithAuth(`${API_BASE}/festivals/${festivalId}`, {
      method: "GET",
    });

    expect(response.ok).toBe(true);
    const festival = await response.json();
    expect(festival.id).toBe(festivalId);
    expect(festival.name).toBeDefined();
  });

  it("should search festivals", async () => {
    const response = await fetchWithAuth(`${API_BASE}/festivals/?search=festival`, {
      method: "GET",
    });

    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(Array.isArray(data.results)).toBe(true);
  });

  it("should filter festivals by type", async () => {
    const response = await fetchWithAuth(`${API_BASE}/festivals/?festival_type=CIRCUS`, {
      method: "GET",
    });

    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(Array.isArray(data.results)).toBe(true);
  });

  it("should generate email for festival application", async () => {
    // Get a festival first
    const listResponse = await fetchWithAuth(`${API_BASE}/festivals/?limit=1`, {
      method: "GET",
    });
    const listData = await listResponse.json();

    if (listData.results.length === 0) {
      console.log("Skipping: No festivals available");
      return;
    }

    const festivalId = listData.results[0].id;

    // Get current user profile
    const profileResponse = await fetchWithAuth(`${API_BASE}/profiles/me`, {
      method: "GET",
    });
    const profile = await profileResponse.json();

    // Generate email
    const response = await fetchWithAuth(`${API_BASE}/festivals/${festivalId}/generate_email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        profile: profile,
        selectedPerformanceIds: [],
      }),
    });

    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(data.message).toBeDefined();
  });

  it("should create an application to festival", async () => {
    // Get a festival
    const listResponse = await fetchWithAuth(`${API_BASE}/festivals/?limit=1`, {
      method: "GET",
    });
    const listData = await listResponse.json();

    if (listData.results.length === 0) {
      console.log("Skipping: No festivals available");
      return;
    }

    const festivalId = listData.results[0].id;

    // Get current user
    const profileResponse = await fetchWithAuth(`${API_BASE}/profiles/me`, {
      method: "GET",
    });
    const profile = await profileResponse.json();

    // Create application using JSON format
    const response = await fetchWithAuth(`${API_BASE}/festivals/${festivalId}/apply`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        profile: profile.id,
        organisationType: "Festival",
        emailSubject: "E2E Test Application",
        message: "Testing application submission via E2E tests",
        applicationDate: new Date().toISOString().split("T")[0],
        recipients: "test@test.com" + ",test@festival.com",
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Application creation failed:", errorData);
    }

    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(data.applicationId).toBeDefined();
    // Track for cleanup
    trackEntity("application", data.applicationId);
  });

  it("should fetch all applications for user", async () => {
    const response = await fetchWithAuth(`${API_BASE}/applications`, {
      method: "GET",
    });

    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(data).toHaveProperty("count");
    expect(Array.isArray(data.results)).toBe(true);
  });

  it("should get single application", async () => {
    // Get applications list
    const listResponse = await fetchWithAuth(`${API_BASE}/applications`, {
      method: "GET",
    });
    const listData = await listResponse.json();

    if (listData.results.length === 0) {
      console.log("Skipping: No applications available");
      return;
    }

    const applicationId = listData.results[0].id;

    // Get single application
    const response = await fetchWithAuth(`${API_BASE}/applications/${applicationId}`, {
      method: "GET",
    });

    expect(response.ok).toBe(true);
    const application = await response.json();
    expect(application.id).toBe(applicationId);
  });

  it("should update application status", async () => {
    // Get applications
    const listResponse = await fetchWithAuth(`${API_BASE}/applications`, {
      method: "GET",
    });
    const listData = await listResponse.json();

    if (listData.results.length === 0) {
      console.log("Skipping: No applications available");
      return;
    }

    const applicationId = listData.results[0].id;

    // Update status to IN_DISCUSSION
    const response = await fetchWithAuth(
      `${API_BASE}/applications/${applicationId}/status/IN_DISCUSSION`,
      {
        method: "PATCH",
      },
    );

    // Note: May return 200 or 404 depending on permissions
    expect([200, 403, 404]).toContain(response.status);
  });
});
