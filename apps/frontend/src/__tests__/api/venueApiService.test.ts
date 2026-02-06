import { describe, it, expect, beforeEach } from 'vitest';
import { venueApiService } from '@/api/venueApiService';
import { Venue, VenueType } from '@/interfaces/entities/Venue';
import { PaginatedResponse } from '@/interfaces/table/PaginatedResponse';
import { TagAction } from '@/interfaces/Enums';
import {
  mockFetchRequest,
  mockSendRequest,
  mockDeleteRequest,
  mockPatchRequest,
  resetAllMocks,
} from '../mocks/fetchHelper';

describe('venueApiService', () => {
  beforeEach(() => {
    resetAllMocks();
  });

  describe('getAll', () => {
    it('should fetch all venues without params', async () => {
      const mockData: PaginatedResponse<Venue> = {
        count: 2,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            name: 'National Theatre',
            country: 'UK',
            town: 'London',
            venueType: VenueType.THEATRE,
          },
          {
            id: 2,
            name: 'Concert Hall',
            country: 'Austria',
            town: 'Vienna',
            venueType: VenueType.CONCERT_HALL,
          },
        ],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await venueApiService.getAll();

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result.results).toHaveLength(2);
    });

    it('should fetch venues with pagination', async () => {
      const mockData: PaginatedResponse<Venue> = {
        count: 50,
        next: 'http://api/venues/?offset=20',
        previous: 'http://api/venues/?offset=0',
        results: [],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await venueApiService.getAll({
        offset: 10,
        limit: 10,
      });

      expect(result.count).toBe(50);
    });

    it('should fetch venues with search filter', async () => {
      const mockData: PaginatedResponse<Venue> = {
        count: 1,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            name: 'National Theatre',
            country: 'UK',
          },
        ],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await venueApiService.getAll({
        search: 'Theatre',
      });

      expect(result.results).toHaveLength(1);
      expect(result.results[0].name).toBe('National Theatre');
    });
  });

  describe('get', () => {
    it('should fetch a single venue by ID', async () => {
      const mockVenue: Venue = {
        id: 1,
        name: 'National Theatre',
        country: 'UK',
        town: 'London',
        venueType: VenueType.THEATRE,
        websiteUrl: 'https://nationaltheatre.com',
        contacts: [],
      };

      mockFetchRequest.mockResolvedValue(mockVenue);

      const result = await venueApiService.get(1);

      expect(mockFetchRequest).toHaveBeenCalledWith('/api/venues/1/');
      expect(result.name).toBe('National Theatre');
    });

    it('should handle venue not found', async () => {
      const error = new Error('Not found');
      mockFetchRequest.mockRejectedValue(error);

      await expect(venueApiService.get(999)).rejects.toThrow('Not found');
    });
  });

  describe('create', () => {
    it('should create a new venue', async () => {
      const newVenue: Venue = {
        id: 3,
        name: 'Opera House',
        country: 'Italy',
        town: 'Milan',
        venueType: VenueType.OPERA_HOUSE,
      };

      mockSendRequest.mockResolvedValue(newVenue);

      const result = await venueApiService.create(newVenue);

      expect(mockSendRequest).toHaveBeenCalledWith(
        '/api/venues/',
        newVenue,
        'POST',
        'Venue successfully created'
      );
      expect(result.venueType).toBe(VenueType.OPERA_HOUSE);
    });

    it('should create venue with contacts', async () => {
      const venueWithContacts: Venue = {
        id: 4,
        name: 'Dance Studio',
        country: 'Spain',
        contacts: [
          {
            id: 1,
            email: 'director@studio.com',
            firstName: 'Maria',
            lastName: 'Garcia',
          },
        ],
      };

      mockSendRequest.mockResolvedValue(venueWithContacts);

      const result = await venueApiService.create(venueWithContacts);

      expect(result.contacts).toHaveLength(1);
      expect(result.contacts?.[0].email).toBe('director@studio.com');
    });

    it('should create circus venue', async () => {
      const circusVenue: Venue = {
        id: 5,
        name: 'Big Top Circus',
        country: 'France',
        town: 'Lyon',
        venueType: VenueType.CIRCUS_TENT,
      };

      mockSendRequest.mockResolvedValue(circusVenue);

      const result = await venueApiService.create(circusVenue);

      expect(result.venueType).toBe(VenueType.CIRCUS_TENT);
    });
  });

  describe('update', () => {
    it('should update an existing venue', async () => {
      const updatedVenue: Venue = {
        id: 1,
        name: 'Updated National Theatre',
        country: 'UK',
        town: 'London',
        venueType: VenueType.THEATRE,
      };

      mockSendRequest.mockResolvedValue(updatedVenue);

      const result = await venueApiService.update(updatedVenue);

      expect(mockSendRequest).toHaveBeenCalledWith(
        '/api/venues/1/',
        updatedVenue,
        'PUT',
        'Venue successfully updated'
      );
      expect(result.name).toBe('Updated National Theatre');
    });

    it('should update venue type', async () => {
      const venue: Venue = {
        id: 2,
        name: 'Concert Hall',
        venueType: VenueType.MUSIC_VENUE,
      };

      mockSendRequest.mockResolvedValue(venue);

      const result = await venueApiService.update(venue);

      expect(result.venueType).toBe(VenueType.MUSIC_VENUE);
    });

    it('should mark venue as contacted', async () => {
      const venue: Venue = {
        id: 3,
        name: 'Opera House',
        contacted: true,
      };

      mockSendRequest.mockResolvedValue(venue);

      const result = await venueApiService.update(venue);

      expect(result.contacted).toBe(true);
    });
  });

  describe('remove', () => {
    it('should delete a venue', async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await venueApiService.remove(1);

      expect(mockDeleteRequest).toHaveBeenCalledWith(
        '/api/venues/1',
        'Venue successfully deleted'
      );
    });

    it('should handle deletion error', async () => {
      const error = new Error('Not found');
      mockDeleteRequest.mockRejectedValue(error);

      await expect(venueApiService.remove(999)).rejects.toThrow('Not found');
    });
  });

  describe('tag', () => {
    it('should tag a venue with STAR action', async () => {
      const taggedVenue: Venue = {
        id: 1,
        name: 'National Theatre',
        tag: 'STAR',
      };

      mockPatchRequest.mockResolvedValue(taggedVenue);

      const result = await venueApiService.tag(1, TagAction.STAR);

      expect(mockPatchRequest).toHaveBeenCalledWith(
        '/api/venues/1/tag/STAR/',
        'Venue successfully tagged'
      );
      expect(result.tag).toBe('STAR');
    });

    it('should tag a venue with WATCH action', async () => {
      const taggedVenue: Venue = {
        id: 2,
        name: 'Concert Hall',
        tag: 'WATCH',
      };

      mockPatchRequest.mockResolvedValue(taggedVenue);

      const result = await venueApiService.tag(2, TagAction.WATCH);

      expect(result.tag).toBe('WATCH');
    });

    it('should tag a venue with INACTIVE action', async () => {
      const taggedVenue: Venue = {
        id: 3,
        name: 'Closed Venue',
        tag: 'INACTIVE',
      };

      mockPatchRequest.mockResolvedValue(taggedVenue);

      const result = await venueApiService.tag(3, TagAction.INACTIVE);

      expect(result.tag).toBe('INACTIVE');
    });
  });

  describe('enrich', () => {
    it('should enrich a venue with additional data', async () => {
      const enrichedVenue: Venue = {
        id: 1,
        name: 'National Theatre',
        country: 'UK',
        town: 'London',
        description: 'Historic theatre in London',
        contacts: [],
      };

      mockFetchRequest.mockResolvedValue(enrichedVenue);

      const result = await venueApiService.enrich(1);

      expect(mockFetchRequest).toHaveBeenCalledWith('/api/venues/1/enrich/');
      expect(result.description).toBeDefined();
    });
  });

  describe('generateEmail', () => {
    it('should generate email for a venue', async () => {
      const response = { message: 'Email generated successfully' };

      mockSendRequest.mockResolvedValue(response);

      const result = await venueApiService.generateEmail(1);

      expect(mockSendRequest).toHaveBeenCalled();
      expect(result.message).toBe('Email generated successfully');
    });
  });

  describe('Complex scenarios', () => {
    it('should handle venue with all optional fields', async () => {
      const fullVenue: Venue = {
        id: 1,
        name: 'Complete Venue',
        websiteUrl: 'https://venue.com',
        country: 'France',
        town: 'Paris',
        approximateDate: '2025-06-01',
        venueType: VenueType.PERFORMANCE_SPACE,
        contacted: true,
        description: 'Amazing performance space',
        comments: 'Perfect for circus acts',
        tag: 'STAR',
        contacts: [
          {
            id: 1,
            email: 'manager@venue.com',
            firstName: 'Antoine',
            lastName: 'Dupont',
          },
        ],
      };

      mockSendRequest.mockResolvedValue(fullVenue);

      const result = await venueApiService.create(fullVenue);

      expect(result.websiteUrl).toBe('https://venue.com');
      expect(result.contacted).toBe(true);
      expect(result.contacts).toHaveLength(1);
    });

    it('should handle venue with minimal fields', async () => {
      const minimalVenue: Venue = {
        id: 2,
        name: 'Minimal Venue',
      };

      mockSendRequest.mockResolvedValue(minimalVenue);

      const result = await venueApiService.create(minimalVenue);

      expect(result.id).toBe(2);
      expect(result.name).toBe('Minimal Venue');
    });

    it('should handle filtering by venue type', async () => {
      const theatreVenues: PaginatedResponse<Venue> = {
        count: 5,
        next: null,
        previous: null,
        results: Array.from({ length: 5 }, (_, i) => ({
          id: i + 1,
          name: `Theatre ${i + 1}`,
          venueType: VenueType.THEATRE,
        })),
      };

      mockFetchRequest.mockResolvedValue(theatreVenues);

      const result = await venueApiService.getAll({
        columnFilters: {
          venueType: [VenueType.THEATRE],
        },
      });

      expect(result.results.every((v) => v.venueType === VenueType.THEATRE)).toBe(true);
    });
  });
});
