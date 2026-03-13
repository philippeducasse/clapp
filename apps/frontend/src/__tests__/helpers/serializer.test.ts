import { describe, it, expect } from "vitest";
import { transformKeysToCamelCase, transformKeysToSnakeCase } from "@/utils/stringUtils";

describe("Serializer - transformKeysToCamelCase", () => {
  it("should convert simple snake_case keys to camelCase", () => {
    const input = { first_name: "John", last_name: "Doe" };
    const expected = { firstName: "John", lastName: "Doe" };
    expect(transformKeysToCamelCase(input)).toEqual(expected);
  });

  it("should handle nested objects", () => {
    const input = {
      user_profile: {
        first_name: "John",
        last_name: "Doe",
      },
    };
    const expected = {
      userProfile: {
        firstName: "John",
        lastName: "Doe",
      },
    };
    expect(transformKeysToCamelCase(input)).toEqual(expected);
  });

  it("should handle deeply nested objects", () => {
    const input = {
      user_data: {
        contact_info: {
          email_address: "john@example.com",
          phone_number: "123-456-7890",
        },
      },
    };
    const expected = {
      userData: {
        contactInfo: {
          emailAddress: "john@example.com",
          phoneNumber: "123-456-7890",
        },
      },
    };
    expect(transformKeysToCamelCase(input)).toEqual(expected);
  });

  it("should handle arrays of objects", () => {
    const input = [
      { first_name: "John", last_name: "Doe" },
      { first_name: "Jane", last_name: "Smith" },
    ];
    const expected = [
      { firstName: "John", lastName: "Doe" },
      { firstName: "Jane", lastName: "Smith" },
    ];
    expect(transformKeysToCamelCase(input)).toEqual(expected);
  });

  it("should handle nested arrays within objects", () => {
    const input = {
      user_list: [
        { first_name: "John", last_name: "Doe" },
        { first_name: "Jane", last_name: "Smith" },
      ],
    };
    const expected = {
      userList: [
        { firstName: "John", lastName: "Doe" },
        { firstName: "Jane", lastName: "Smith" },
      ],
    };
    expect(transformKeysToCamelCase(input)).toEqual(expected);
  });

  it("should preserve primitive values (strings, numbers, booleans)", () => {
    const input = {
      string_val: "text",
      number_val: 42,
      boolean_val: true,
      null_val: null,
    };
    const expected = {
      stringVal: "text",
      numberVal: 42,
      booleanVal: true,
      nullVal: null,
    };
    expect(transformKeysToCamelCase(input)).toEqual(expected);
  });

  it("should handle empty objects", () => {
    expect(transformKeysToCamelCase({})).toEqual({});
  });

  it("should handle empty arrays", () => {
    expect(transformKeysToCamelCase([])).toEqual([]);
  });

  it("should handle null", () => {
    expect(transformKeysToCamelCase(null)).toBeNull();
  });

  it("should handle undefined", () => {
    expect(transformKeysToCamelCase(undefined)).toBeUndefined();
  });

  it("should handle primitive values", () => {
    expect(transformKeysToCamelCase("string")).toBe("string");
    expect(transformKeysToCamelCase(42)).toBe(42);
    expect(transformKeysToCamelCase(true)).toBe(true);
  });

  it("should handle objects with multiple underscores in keys", () => {
    const input = { very_long_key_name: "value" };
    const expected = { veryLongKeyName: "value" };
    expect(transformKeysToCamelCase(input)).toEqual(expected);
  });

  it("should handle mixed keys (already camelCase and snake_case)", () => {
    const input = {
      firstName: "John",
      last_name: "Doe",
      middle_name: "Michael",
    };
    // Note: lodash camelCase doesn't change already camelCase keys
    const result = transformKeysToCamelCase(input);
    expect(result.firstName).toBe("John");
    expect(result.lastName).toBe("Doe");
    expect(result.middleName).toBe("Michael");
  });

  it("should handle objects with special values (dates as strings)", () => {
    const input = {
      created_at: "2025-01-15T10:30:00Z",
      updated_at: "2025-02-06T14:22:00Z",
    };
    const expected = {
      createdAt: "2025-01-15T10:30:00Z",
      updatedAt: "2025-02-06T14:22:00Z",
    };
    expect(transformKeysToCamelCase(input)).toEqual(expected);
  });

  it("should handle arrays of primitive values", () => {
    const input = {
      numbers: [1, 2, 3],
      strings: ["a", "b", "c"],
    };
    const expected = {
      numbers: [1, 2, 3],
      strings: ["a", "b", "c"],
    };
    expect(transformKeysToCamelCase(input)).toEqual(expected);
  });

  it("should handle complex nested structures with arrays and objects", () => {
    const input = {
      user_data: {
        personal_info: {
          first_name: "John",
          last_name: "Doe",
        },
        contact_methods: [
          { contact_type: "email", contact_value: "john@example.com" },
          { contact_type: "phone", contact_value: "123-456-7890" },
        ],
      },
    };
    const expected = {
      userData: {
        personalInfo: {
          firstName: "John",
          lastName: "Doe",
        },
        contactMethods: [
          { contactType: "email", contactValue: "john@example.com" },
          { contactType: "phone", contactValue: "123-456-7890" },
        ],
      },
    };
    expect(transformKeysToCamelCase(input)).toEqual(expected);
  });
});

describe("Serializer - transformKeysToSnakeCase", () => {
  it("should convert simple camelCase keys to snake_case", () => {
    const input = { firstName: "John", lastName: "Doe" };
    const expected = { first_name: "John", last_name: "Doe" };
    expect(transformKeysToSnakeCase(input)).toEqual(expected);
  });

  it("should handle nested objects", () => {
    const input = {
      userProfile: {
        firstName: "John",
        lastName: "Doe",
      },
    };
    const expected = {
      user_profile: {
        first_name: "John",
        last_name: "Doe",
      },
    };
    expect(transformKeysToSnakeCase(input)).toEqual(expected);
  });

  it("should handle deeply nested objects", () => {
    const input = {
      userData: {
        contactInfo: {
          emailAddress: "john@example.com",
          phoneNumber: "123-456-7890",
        },
      },
    };
    const expected = {
      user_data: {
        contact_info: {
          email_address: "john@example.com",
          phone_number: "123-456-7890",
        },
      },
    };
    expect(transformKeysToSnakeCase(input)).toEqual(expected);
  });

  it("should handle arrays of objects", () => {
    const input = [
      { firstName: "John", lastName: "Doe" },
      { firstName: "Jane", lastName: "Smith" },
    ];
    const expected = [
      { first_name: "John", last_name: "Doe" },
      { first_name: "Jane", last_name: "Smith" },
    ];
    expect(transformKeysToSnakeCase(input)).toEqual(expected);
  });

  it("should handle nested arrays within objects", () => {
    const input = {
      userList: [
        { firstName: "John", lastName: "Doe" },
        { firstName: "Jane", lastName: "Smith" },
      ],
    };
    const expected = {
      user_list: [
        { first_name: "John", last_name: "Doe" },
        { first_name: "Jane", last_name: "Smith" },
      ],
    };
    expect(transformKeysToSnakeCase(input)).toEqual(expected);
  });

  it("should preserve primitive values (strings, numbers, booleans)", () => {
    const input = {
      stringVal: "text",
      numberVal: 42,
      booleanVal: true,
      nullVal: null,
    };
    const expected = {
      string_val: "text",
      number_val: 42,
      boolean_val: true,
      null_val: null,
    };
    expect(transformKeysToSnakeCase(input)).toEqual(expected);
  });

  it("should handle empty objects", () => {
    expect(transformKeysToSnakeCase({})).toEqual({});
  });

  it("should handle empty arrays", () => {
    expect(transformKeysToSnakeCase([])).toEqual([]);
  });

  it("should handle null", () => {
    expect(transformKeysToSnakeCase(null)).toBeNull();
  });

  it("should handle undefined", () => {
    expect(transformKeysToSnakeCase(undefined)).toBeUndefined();
  });

  it("should handle primitive values", () => {
    expect(transformKeysToSnakeCase("string")).toBe("string");
    expect(transformKeysToSnakeCase(42)).toBe(42);
    expect(transformKeysToSnakeCase(true)).toBe(true);
  });

  it("should handle objects with multiple capital letters", () => {
    const input = { veryLongKeyName: "value" };
    const expected = { very_long_key_name: "value" };
    expect(transformKeysToSnakeCase(input)).toEqual(expected);
  });

  it("should handle mixed keys (snake_case and camelCase)", () => {
    const input = {
      first_name: "John",
      lastName: "Doe",
      middleName: "Michael",
    };
    const result = transformKeysToSnakeCase(input);
    expect(result.first_name).toBe("John");
    expect(result.last_name).toBe("Doe");
    expect(result.middle_name).toBe("Michael");
  });

  it("should handle objects with special values (dates as strings)", () => {
    const input = {
      createdAt: "2025-01-15T10:30:00Z",
      updatedAt: "2025-02-06T14:22:00Z",
    };
    const expected = {
      created_at: "2025-01-15T10:30:00Z",
      updated_at: "2025-02-06T14:22:00Z",
    };
    expect(transformKeysToSnakeCase(input)).toEqual(expected);
  });

  it("should handle arrays of primitive values", () => {
    const input = {
      numbers: [1, 2, 3],
      strings: ["a", "b", "c"],
    };
    const expected = {
      numbers: [1, 2, 3],
      strings: ["a", "b", "c"],
    };
    expect(transformKeysToSnakeCase(input)).toEqual(expected);
  });

  it("should handle complex nested structures with arrays and objects", () => {
    const input = {
      userData: {
        personalInfo: {
          firstName: "John",
          lastName: "Doe",
        },
        contactMethods: [
          { contactType: "email", contactValue: "john@example.com" },
          { contactType: "phone", contactValue: "123-456-7890" },
        ],
      },
    };
    const expected = {
      user_data: {
        personal_info: {
          first_name: "John",
          last_name: "Doe",
        },
        contact_methods: [
          { contact_type: "email", contact_value: "john@example.com" },
          { contact_type: "phone", contact_value: "123-456-7890" },
        ],
      },
    };
    expect(transformKeysToSnakeCase(input)).toEqual(expected);
  });
});

describe("Serializer - Bidirectional Transformation", () => {
  it("should be reversible: camelCase -> snakeCase -> camelCase", () => {
    const original = {
      firstName: "John",
      lastName: "Doe",
      emailAddress: "john@example.com",
    };
    const snakeVersion = transformKeysToSnakeCase(original);
    const backToCamel = transformKeysToCamelCase(snakeVersion);
    expect(backToCamel).toEqual(original);
  });

  it("should be reversible with nested objects", () => {
    const original = {
      userData: {
        personalInfo: {
          firstName: "John",
          lastName: "Doe",
        },
      },
    };
    const snakeVersion = transformKeysToSnakeCase(original);
    const backToCamel = transformKeysToCamelCase(snakeVersion);
    expect(backToCamel).toEqual(original);
  });

  it("should be reversible with arrays of objects", () => {
    const original = [
      { firstName: "John", lastName: "Doe" },
      { firstName: "Jane", lastName: "Smith" },
    ];
    const snakeVersion = transformKeysToSnakeCase(original);
    const backToCamel = transformKeysToCamelCase(snakeVersion);
    expect(backToCamel).toEqual(original);
  });

  it("should be reversible with complex nested structures", () => {
    const original = {
      userData: {
        personalInfo: {
          firstName: "John",
          lastName: "Doe",
        },
        contactMethods: [
          { contactType: "email", contactValue: "john@example.com" },
          { contactType: "phone", contactValue: "123-456-7890" },
        ],
      },
    };
    const snakeVersion = transformKeysToSnakeCase(original);
    const backToCamel = transformKeysToCamelCase(snakeVersion);
    expect(backToCamel).toEqual(original);
  });

  it("should handle real-world API response structure", () => {
    const apiResponse = {
      id: 1,
      created_at: "2025-01-15T10:30:00Z",
      updated_at: "2025-02-06T14:22:00Z",
      user_profile: {
        first_name: "John",
        last_name: "Doe",
        email_address: "john@example.com",
      },
      festival_applications: [
        {
          application_id: 101,
          festival_name: "Jazz Festival",
          application_status: "accepted",
        },
        {
          application_id: 102,
          festival_name: "Rock Festival",
          application_status: "pending",
        },
      ],
    };

    // Simulate API response -> Frontend conversion
    const frontendData = transformKeysToCamelCase(apiResponse);
    expect(frontendData).toEqual({
      id: 1,
      createdAt: "2025-01-15T10:30:00Z",
      updatedAt: "2025-02-06T14:22:00Z",
      userProfile: {
        firstName: "John",
        lastName: "Doe",
        emailAddress: "john@example.com",
      },
      festivalApplications: [
        {
          applicationId: 101,
          festivalName: "Jazz Festival",
          applicationStatus: "accepted",
        },
        {
          applicationId: 102,
          festivalName: "Rock Festival",
          applicationStatus: "pending",
        },
      ],
    });

    // Simulate Frontend -> API request conversion
    const backendData = transformKeysToSnakeCase(frontendData);
    expect(backendData).toEqual(apiResponse);
  });
});
