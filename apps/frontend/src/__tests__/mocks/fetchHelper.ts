// Re-export mocks from setup file
// The actual vi.mock() setup happens in setup.ts which runs before tests
export {
  mockFetchRequest,
  mockSendRequest,
  mockDeleteRequest,
  mockPatchRequest,
  mockSendFormDataRequest,
  mockSilentRequest,
  resetAllMocks,
} from '../setup';
