import { describe, it, expect, beforeEach } from 'vitest';
import { residencyApiService } from '@/api/residencyApiService';
import { Residency } from '@/interfaces/entities/Residency';
import { PaginatedResponse } from '@/interfaces/table/PaginatedResponse';
import { TagAction } from '@/interfaces/Enums';
import {
  mockFetchRequest,
  mockSendRequest,
  mockDeleteRequest,
  mockPatchRequest,
  resetAllMocks,
} from '../mocks/fetchHelper';

describe('residencyApiService', () => {
  beforeEach(() => {
    resetAllMocks();
  });

  describe('getAll', () => {
    it('should fetch all residencies without params', async () => {
      const mockData: PaginatedResponse<Residency> = {
        count: 2,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            name: 'Berlin Residency',
            location: 'Berlin',
            country: 'Germany',
            town: 'Berlin',
          },
          {
            id: 2,
            name: 'Paris Residency',
            location: 'Paris',
            country: 'France',
            town: 'Paris',
          },
        ],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await residencyApiService.getAll();

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result.results).toHaveLength(2);
    });

    it('should fetch residencies with pagination', async () => {
      const mockData: PaginatedResponse<Residency> = {
        count: 100,
        next: 'http://api/residencies/?offset=10',
        previous: null,
        results: [],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await residencyApiService.getAll({
        offset: 0,
        limit: 10,
      });

      expect(result.count).toBe(100);
    });

    it('should fetch residencies with search filter', async () => {
      const mockData: PaginatedResponse<Residency> = {
        count: 1,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            name: 'Berlin Residency',
            location: 'Berlin',
          },
        ],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await residencyApiService.getAll({
        search: 'Berlin',
      });

      expect(result.results).toHaveLength(1);
      expect(result.results[0].name).toBe('Berlin Residency');
    });
  });

  describe('get', () => {
    it('should fetch a single residency by ID', async () => {
      const mockResidency: Residency = {
        id: 1,
        name: 'Berlin Residency',
        location: 'Berlin',
        country: 'Germany',
        town: 'Berlin',
        websiteUrl: 'https://berlinresidency.com',
        contacts: [],
      };

      mockFetchRequest.mockResolvedValue(mockResidency);

      const result = await residencyApiService.get(1);

      expect(mockFetchRequest).toHaveBeenCalledWith('/api/residencies/1');
      expect(result.name).toBe('Berlin Residency');
    });

    it('should handle residency not found', async () => {
      const error = new Error('Not found');
      mockFetchRequest.mockRejectedValue(error);

      await expect(residencyApiService.get(999)).rejects.toThrow('Not found');
    });
  });

  describe('create', () => {
    it('should create a new residency', async () => {
      const newResidency: Residency = {
        id: 3,
        name: 'New Residency',
        location: 'Amsterdam',
        country: 'Netherlands',
        town: 'Amsterdam',
      };

      mockSendRequest.mockResolvedValue(newResidency);

      const result = await residencyApiService.create(newResidency);

      expect(mockSendRequest).toHaveBeenCalledWith(
        '/api/residencies',
        newResidency,
        'POST',
        'Residency successfully created'
      );
      expect(result.location).toBe('Amsterdam');
    });

    it('should create residency with dates', async () => {
      const residencyWithDates: Residency = {
        id: 4,
        name: 'Summer Residency',
        location: 'Barcelona',
        country: 'Spain',
        startDate: '2025-06-01',
        endDate: '2025-08-31',
      };

      mockSendRequest.mockResolvedValue(residencyWithDates);

      const result = await residencyApiService.create(residencyWithDates);

      expect(result.startDate).toBe('2025-06-01');
      expect(result.endDate).toBe('2025-08-31');
    });

    it('should create residency with contacts', async () => {
      const residencyWithContacts: Residency = {
        id: 5,
        name: 'Vienna Residency',
        location: 'Vienna',
        country: 'Austria',
        contacts: [
          {
            id: 1,
            email: 'coordinator@residency.com',
            firstName: 'Klaus',
            lastName: 'Mueller',
          },
        ],
      };

      mockSendRequest.mockResolvedValue(residencyWithContacts);

      const result = await residencyApiService.create(residencyWithContacts);

      expect(result.contacts).toHaveLength(1);
      expect(result.contacts?.[0].email).toBe('coordinator@residency.com');
    });

    it('should create residency with application dates', async () => {
      const residency: Residency = {
        id: 6,
        name: 'Application Residency',
        location: 'Prague',
        applicationType: 'FORM',
        applicationStart: '2025-01-01',
        applicationEnd: '2025-05-31',
      };

      mockSendRequest.mockResolvedValue(residency);

      const result = await residencyApiService.create(residency);

      expect(result.applicationType).toBe('FORM');
      expect(result.applicationStart).toBe('2025-01-01');
    });
  });

  describe('update', () => {
    it('should update an existing residency', async () => {
      const updatedResidency: Residency = {
        id: 1,
        name: 'Updated Berlin Residency',
        location: 'Berlin',
        country: 'Germany',
      };

      mockSendRequest.mockResolvedValue(updatedResidency);

      const result = await residencyApiService.update(updatedResidency);

      expect(mockSendRequest).toHaveBeenCalledWith(
        '/api/residencies/1',
        updatedResidency,
        'PUT',
        'Residency successfully updated'
      );
      expect(result.name).toBe('Updated Berlin Residency');
    });

    it('should update residency dates', async () => {
      const residency: Residency = {
        id: 2,
        name: 'Paris Residency',
        startDate: '2025-07-01',
        endDate: '2025-09-30',
      };

      mockSendRequest.mockResolvedValue(residency);

      const result = await residencyApiService.update(residency);

      expect(result.startDate).toBe('2025-07-01');
      expect(result.endDate).toBe('2025-09-30');
    });

    it('should update residency with applied status', async () => {
      const residency: Residency = {
        id: 3,
        name: 'Amsterdam Residency',
        applied: true,
      };

      mockSendRequest.mockResolvedValue(residency);

      const result = await residencyApiService.update(residency);

      expect(result.applied).toBe(true);
    });

    it('should update residency status', async () => {
      const residency: Residency = {
        id: 4,
        name: 'Barcelona Residency',
        status: 'CONFIRMED',
      };

      mockSendRequest.mockResolvedValue(residency);

      const result = await residencyApiService.update(residency);

      expect(result.status).toBe('CONFIRMED');
    });
  });

  describe('remove', () => {
    it('should delete a residency', async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await residencyApiService.remove(1);

      expect(mockDeleteRequest).toHaveBeenCalledWith(
        '/api/residencies/1',
        'Residency successfully deleted'
      );
    });

    it('should handle deletion error', async () => {
      const error = new Error('Not found');
      mockDeleteRequest.mockRejectedValue(error);

      await expect(residencyApiService.remove(999)).rejects.toThrow('Not found');
    });

    it('should delete multiple residencies in sequence', async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await residencyApiService.remove(1);
      await residencyApiService.remove(2);
      await residencyApiService.remove(3);

      expect(mockDeleteRequest).toHaveBeenCalledTimes(3);
    });
  });

  describe('tag', () => {
    it('should tag a residency with STAR action', async () => {
      const taggedResidency: Residency = {
        id: 1,
        name: 'Berlin Residency',
        tag: 'STAR',
      };

      mockPatchRequest.mockResolvedValue(taggedResidency);

      const result = await residencyApiService.tag(1, TagAction.STAR);

      expect(mockPatchRequest).toHaveBeenCalledWith(
        '/api/residencies/1/tag/STAR',
        'Residency successfully tagged'
      );
      expect(result.tag).toBe('STAR');
    });

    it('should tag a residency with WATCH action', async () => {
      const taggedResidency: Residency = {
        id: 2,
        name: 'Paris Residency',
        tag: 'WATCH',
      };

      mockPatchRequest.mockResolvedValue(taggedResidency);

      const result = await residencyApiService.tag(2, TagAction.WATCH);

      expect(result.tag).toBe('WATCH');
    });

    it('should tag a residency with INACTIVE action', async () => {
      const taggedResidency: Residency = {
        id: 3,
        name: 'Closed Residency',
        tag: 'INACTIVE',
      };

      mockPatchRequest.mockResolvedValue(taggedResidency);

      const result = await residencyApiService.tag(3, TagAction.INACTIVE);

      expect(result.tag).toBe('INACTIVE');
    });
  });

  describe('enrich', () => {
    it('should enrich a residency with additional data', async () => {
      const enrichedResidency: Residency = {
        id: 1,
        name: 'Berlin Residency',
        location: 'Berlin',
        description: 'Artist residency in Berlin',
        contacts: [],
      };

      mockFetchRequest.mockResolvedValue(enrichedResidency);

      const result = await residencyApiService.enrich(1);

      expect(mockFetchRequest).toHaveBeenCalledWith('/api/residencies/1/enrich');
      expect(result.description).toBeDefined();
    });
  });

  describe('generateEmail', () => {
    it('should generate email for a residency', async () => {
      const response = { message: 'Email generated successfully' };

      mockSendRequest.mockResolvedValue(response);

      const result = await residencyApiService.generateEmail(1);

      expect(mockSendRequest).toHaveBeenCalled();
      expect(result.message).toBe('Email generated successfully');
    });
  });

  describe('Complex scenarios', () => {
    it('should handle residency with all optional fields', async () => {
      const fullResidency: Residency = {
        id: 1,
        name: 'Complete Residency',
        location: 'Vienna',
        website: 'https://residency.at',
        websiteUrl: 'https://residency.at',
        country: 'Austria',
        town: 'Vienna',
        approximateDate: '2025-06-01',
        startDate: '2025-06-01',
        endDate: '2025-08-31',
        applicationType: 'FORM',
        applicationStart: '2025-01-01',
        applicationEnd: '2025-05-31',
        applied: true,
        description: 'Amazing artist residency program',
        comments: 'Perfect for experimental work',
        status: 'CONFIRMED',
        tag: 'STAR',
        lastUpdated: '2025-02-06',
        contacts: [
          {
            id: 1,
            email: 'director@residency.at',
            firstName: 'Wolfgang',
            lastName: 'Schmidt',
          },
        ],
      };

      mockSendRequest.mockResolvedValue(fullResidency);

      const result = await residencyApiService.create(fullResidency);

      expect(result.websiteUrl).toBe('https://residency.at');
      expect(result.startDate).toBe('2025-06-01');
      expect(result.applied).toBe(true);
      expect(result.status).toBe('CONFIRMED');
      expect(result.contacts).toHaveLength(1);
    });

    it('should handle residency with minimal fields', async () => {
      const minimalResidency: Residency = {
        id: 2,
        name: 'Minimal Residency',
      };

      mockSendRequest.mockResolvedValue(minimalResidency);

      const result = await residencyApiService.create(minimalResidency);

      expect(result.id).toBe(2);
      expect(result.name).toBe('Minimal Residency');
    });

    it('should handle date filtering', async () => {
      const futureResidencies: PaginatedResponse<Residency> = {
        count: 3,
        next: null,
        previous: null,
        results: Array.from({ length: 3 }, (_, i) => ({
          id: i + 1,
          name: `Future Residency ${i + 1}`,
          location: `City ${i + 1}`,
          startDate: `2025-${String(i + 7).padStart(2, '0')}-01`,
          endDate: `2025-${String(i + 8).padStart(2, '0')}-31`,
        })),
      };

      mockFetchRequest.mockResolvedValue(futureResidencies);

      const result = await residencyApiService.getAll({
        columnFilters: {
          startDate: ['2025-07-01'],
        },
      });

      expect(result.results).toHaveLength(3);
    });

    it('should handle multiple contacts per residency', async () => {
      const residency: Residency = {
        id: 5,
        name: 'Multi-Contact Residency',
        location: 'Prague',
        contacts: [
          {
            id: 1,
            email: 'director@residency.cz',
            firstName: 'Jan',
            lastName: 'Novak',
          },
          {
            id: 2,
            email: 'admin@residency.cz',
            firstName: 'Maria',
            lastName: 'Svobodova',
          },
          {
            id: 3,
            email: 'applications@residency.cz',
            firstName: 'Pavel',
            lastName: 'Kral',
          },
        ],
      };

      mockSendRequest.mockResolvedValue(residency);

      const result = await residencyApiService.create(residency);

      expect(result.contacts).toHaveLength(3);
      expect(result.contacts?.[0].firstName).toBe('Jan');
      expect(result.contacts?.[2].email).toBe('applications@residency.cz');
    });
  });
});
