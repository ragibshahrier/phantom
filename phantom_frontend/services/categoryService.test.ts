import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import categoryService, { clearCategoryCache } from './categoryService';
import apiClient from '../config/api';
import { Category } from '../types';

// Mock the API client
vi.mock('../config/api');

describe('categoryService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    clearCategoryCache(); // Clear cache before each test
  });

  afterEach(() => {
    vi.restoreAllMocks();
    clearCategoryCache(); // Clear cache after each test
  });

  describe('getCategories', () => {
    it('should call GET /categories/ and return sorted categories', async () => {
      const mockCategories: Category[] = [
        {
          id: 1,
          name: 'Gaming',
          priority_level: 1,
          color: '#00FF00',
          description: 'Gaming activities',
        },
        {
          id: 2,
          name: 'Exam',
          priority_level: 5,
          color: '#FF0000',
          description: 'Exam preparation',
        },
        {
          id: 3,
          name: 'Study',
          priority_level: 4,
          color: '#0000FF',
          description: 'Study sessions',
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockCategories });

      const result = await categoryService.getCategories();

      expect(apiClient.get).toHaveBeenCalledWith('/categories/');
      
      // Verify categories are sorted by priority (highest first)
      expect(result[0].priority_level).toBe(5); // Exam
      expect(result[1].priority_level).toBe(4); // Study
      expect(result[2].priority_level).toBe(1); // Gaming
    });

    it('should return cached categories on second call', async () => {
      const mockCategories: Category[] = [
        {
          id: 1,
          name: 'Study',
          priority_level: 4,
          color: '#0000FF',
          description: 'Study sessions',
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockCategories });

      // First call - should hit API
      const result1 = await categoryService.getCategories();
      expect(apiClient.get).toHaveBeenCalledTimes(1);
      expect(result1).toEqual(mockCategories);

      // Second call - should use cache
      const result2 = await categoryService.getCategories();
      expect(apiClient.get).toHaveBeenCalledTimes(1); // Still only 1 call
      expect(result2).toEqual(mockCategories);
    });

    it('should throw error when fetching categories fails', async () => {
      const errorResponse = {
        response: {
          data: {
            message: 'Failed to fetch categories',
          },
        },
      };

      vi.mocked(apiClient.get).mockRejectedValueOnce(errorResponse);

      await expect(categoryService.getCategories()).rejects.toThrow('Failed to fetch categories');
    });
  });

  describe('getCategory', () => {
    it('should call GET /categories/{id}/', async () => {
      const mockCategory: Category = {
        id: 1,
        name: 'Study',
        priority_level: 4,
        color: '#0000FF',
        description: 'Study sessions',
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockCategory });

      const result = await categoryService.getCategory(1);

      expect(apiClient.get).toHaveBeenCalledWith('/categories/1/');
      expect(result).toEqual(mockCategory);
    });

    it('should return cached category if available', async () => {
      const mockCategories: Category[] = [
        {
          id: 1,
          name: 'Study',
          priority_level: 4,
          color: '#0000FF',
          description: 'Study sessions',
        },
        {
          id: 2,
          name: 'Exam',
          priority_level: 5,
          color: '#FF0000',
          description: 'Exam preparation',
        },
      ];

      // First, populate the cache
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockCategories });
      await categoryService.getCategories();

      // Now get a specific category - should use cache
      const result = await categoryService.getCategory(1);

      // Should only have called API once (for getCategories)
      expect(apiClient.get).toHaveBeenCalledTimes(1);
      expect(result.id).toBe(1);
      expect(result.name).toBe('Study');
    });

    it('should fetch from API if category not in cache', async () => {
      const mockCategories: Category[] = [
        {
          id: 1,
          name: 'Study',
          priority_level: 4,
          color: '#0000FF',
          description: 'Study sessions',
        },
      ];

      const mockCategory: Category = {
        id: 2,
        name: 'Exam',
        priority_level: 5,
        color: '#FF0000',
        description: 'Exam preparation',
      };

      // First, populate the cache with category 1
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockCategories });
      await categoryService.getCategories();

      // Now get category 2 - should fetch from API
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockCategory });
      const result = await categoryService.getCategory(2);

      expect(apiClient.get).toHaveBeenCalledTimes(2);
      expect(apiClient.get).toHaveBeenLastCalledWith('/categories/2/');
      expect(result).toEqual(mockCategory);
    });

    it('should throw error when category not found', async () => {
      const errorResponse = {
        response: {
          data: {
            detail: 'Category not found',
          },
        },
      };

      vi.mocked(apiClient.get).mockRejectedValueOnce(errorResponse);

      await expect(categoryService.getCategory(999)).rejects.toThrow('Category not found');
    });
  });

  describe('cache management', () => {
    it('should clear cache when clearCategoryCache is called', async () => {
      const mockCategories: Category[] = [
        {
          id: 1,
          name: 'Study',
          priority_level: 4,
          color: '#0000FF',
          description: 'Study sessions',
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockCategories });

      // First call - populate cache
      await categoryService.getCategories();
      expect(apiClient.get).toHaveBeenCalledTimes(1);

      // Second call - use cache
      await categoryService.getCategories();
      expect(apiClient.get).toHaveBeenCalledTimes(1);

      // Clear cache
      clearCategoryCache();

      // Third call - should hit API again
      await categoryService.getCategories();
      expect(apiClient.get).toHaveBeenCalledTimes(2);
    });
  });
});
