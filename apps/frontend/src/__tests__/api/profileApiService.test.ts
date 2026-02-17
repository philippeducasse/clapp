import { describe, it, expect, beforeEach } from 'vitest';
import { profileApiService } from '@/api/profileApiService';
import { Profile } from '@/interfaces/entities/Profile';
import { Credentials } from '@/interfaces/api/ApiService';
import {
  mockFetchRequest,
  mockSendRequest,
  mockDeleteRequest,
  resetAllMocks,
} from '../mocks/fetchHelper';

describe('profileApiService', () => {
  beforeEach(() => {
    resetAllMocks();
  });

  describe('get', () => {
    it('should fetch current profile', async () => {
      const mockProfile: Profile = {
        id: 1,
        email: 'user@example.com',
        firstName: 'John',
        lastName: 'Doe',
        companyName: 'Acme Corp',
        confirmedAccount: true,
        performances: [],
      };

      mockFetchRequest.mockResolvedValue(mockProfile);

      const result = await profileApiService.get();

      expect(mockFetchRequest).toHaveBeenCalledWith('/api/profiles/me/');
      expect(result.id).toBe(1);
      expect(result.email).toBe('user@example.com');
    });

    it('should handle profile with all optional fields', async () => {
      const mockProfile: Profile = {
        id: 1,
        email: 'performer@example.com',
        firstName: 'Jane',
        lastName: 'Smith',
        personalWebsite: 'https://jane.com',
        location: 'Berlin, Germany',
        nationality: 'German',
        spokenLanguages: ['English', 'German', 'French'],
        instagramProfile: '@janesmith',
        facebookProfile: 'janesmith',
        youtubeProfile: 'JaneSmithChannel',
        confirmedAccount: true,
        performances: [],
      };

      mockFetchRequest.mockResolvedValue(mockProfile);

      const result = await profileApiService.get();

      expect(result.spokenLanguages).toEqual(['English', 'German', 'French']);
      expect(result.personalWebsite).toBe('https://jane.com');
    });
  });

  describe('register', () => {
    it('should register a new user', async () => {
      const newProfile: Partial<Profile> = {
        email: 'newuser@example.com',
        firstName: 'Alice',
        lastName: 'Johnson',
      };

      const mockResponse: Profile = {
        id: 2,
        email: 'newuser@example.com',
        firstName: 'Alice',
        lastName: 'Johnson',
        confirmedAccount: true,
        performances: [],
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await profileApiService.register(newProfile);

      expect(mockSendRequest).toHaveBeenCalledWith(
        '/api/profiles/register/',
        newProfile,
        'POST',
        'Profile successfully created!',
      );
      expect(result.id).toBe(2);
      expect(result.email).toBe('newuser@example.com');
    });

    it('should handle registration with minimal fields', async () => {
      const minimalProfile: Partial<Profile> = {
        email: 'minimal@example.com',
      };

      const mockResponse: Profile = {
        id: 3,
        email: 'minimal@example.com',
        confirmedAccount: true,
        performances: [],
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await profileApiService.register(minimalProfile);

      expect(result.email).toBe('minimal@example.com');
    });
  });

  describe('update', () => {
    it('should update profile', async () => {
      const updatedProfile: Partial<Profile> = {
        id: 1,
        firstName: 'John',
        lastName: 'Smith',
        location: 'London, UK',
      };

      const mockResponse: Profile = {
        id: 1,
        email: 'user@example.com',
        firstName: 'John',
        lastName: 'Smith',
        location: 'London, UK',
        confirmedAccount: true,
        performances: [],
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await profileApiService.update(updatedProfile);

      expect(mockSendRequest).toHaveBeenCalledWith(
        '/api/profiles/1/',
        updatedProfile,
        'PUT',
        'Profile successfully updated',
        true,
      );
      expect(result.location).toBe('London, UK');
    });

    it('should update social media profiles', async () => {
      const updatedProfile: Partial<Profile> = {
        id: 1,
        instagramProfile: '@newhandle',
        facebookProfile: 'newfacebook',
        tiktokProfile: '@newtiktok',
        youtubeProfile: 'NewYouTubeChannel',
      };

      const mockResponse: Profile = {
        id: 1,
        email: 'user@example.com',
        instagramProfile: '@newhandle',
        facebookProfile: 'newfacebook',
        tiktokProfile: '@newtiktok',
        youtubeProfile: 'NewYouTubeChannel',
        confirmedAccount: true,
        performances: [],
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await profileApiService.update(updatedProfile);

      expect(result.instagramProfile).toBe('@newhandle');
      expect(result.youtubeProfile).toBe('NewYouTubeChannel');
    });
  });

  describe('remove', () => {
    it('should delete profile', async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await profileApiService.remove(1);

      expect(mockDeleteRequest).toHaveBeenCalledWith(
        '/api/profiles/1/',
        'Profile successfully deleted',
        true,
      );
    });

    it('should handle deletion of different profile IDs', async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await profileApiService.remove(42);

      expect(mockDeleteRequest).toHaveBeenCalledWith(
        '/api/profiles/42/',
        'Profile successfully deleted',
        true,
      );
    });
  });

  describe('login', () => {
    it('should login with valid credentials', async () => {
      const credentials: Credentials = {
        email: 'user@example.com',
        password: 'password123',
      };

      const mockResponse: Profile = {
        id: 1,
        email: 'user@example.com',
        firstName: 'John',
        lastName: 'Doe',
        confirmedAccount: true,
        performances: [],
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await profileApiService.login(credentials);

      expect(mockSendRequest).toHaveBeenCalledWith(
        '/api/profiles/login/',
        credentials,
        'POST',
        'Welcome user@example.com, you have successfully logged in',
        true,
      );
      expect(result.id).toBe(1);
    });

    it('should include email in success message', async () => {
      const credentials: Credentials = {
        email: 'jane@example.com',
        password: 'pass456',
      };

      mockSendRequest.mockResolvedValue({
        id: 2,
        email: 'jane@example.com',
        confirmedAccount: true,
        performances: [],
      } as Profile);

      await profileApiService.login(credentials);

      expect(mockSendRequest).toHaveBeenCalledWith(
        '/api/profiles/login/',
        credentials,
        'POST',
        'Welcome jane@example.com, you have successfully logged in',
        true,
      );
    });
  });

  describe('logout', () => {
    it('should logout user', async () => {
      mockSendRequest.mockResolvedValue({});

      await profileApiService.logout();

      expect(mockSendRequest).toHaveBeenCalledWith(
        '/api/profiles/logout/',
        {},
        'POST',
        'Successfully logged out',
        true,
      );
    });
  });
});
