import { vi } from 'vitest';

// Mock fetchHelper before any imports
export const mockFetchRequest = vi.fn();
export const mockSendRequest = vi.fn();
export const mockDeleteRequest = vi.fn();
export const mockPatchRequest = vi.fn();
export const mockSendFormDataRequest = vi.fn();

vi.mock('@/api/fetchHelper', () => ({
  fetchRequest: mockFetchRequest,
  sendRequest: mockSendRequest,
  deleteRequest: mockDeleteRequest,
  patchRequest: mockPatchRequest,
  sendFormDataRequest: mockSendFormDataRequest,
}));

export const resetAllMocks = () => {
  mockFetchRequest.mockReset();
  mockSendRequest.mockReset();
  mockDeleteRequest.mockReset();
  mockPatchRequest.mockReset();
  mockSendFormDataRequest.mockReset();
};