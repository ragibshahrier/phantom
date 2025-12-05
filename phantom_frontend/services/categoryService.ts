import apiClient from '../config/api';
import { Category, CategoryService } from '../types';

/**
 * Category Service
 * Handles all category-related API calls including fetching categories.
 * Implements in-memory caching since categories rarely change.
 */

/**
 * In-memory cache for categories
 * Categories are cached to reduce unnecessary API calls since they rarely change
 */
let categoryCache: Category[] | null = null;
let cacheTimestamp: number | null = null;

/**
 * Cache duration in milliseconds (5 minutes)
 * After this duration, the cache is considered stale and will be refreshed
 */
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Check if the cache is still valid
 * 
 * @returns true if cache exists and is not stale, false otherwise
 */
const isCacheValid = (): boolean => {
  if (!categoryCache || !cacheTimestamp) {
    return false;
  }
  
  const now = Date.now();
  return (now - cacheTimestamp) < CACHE_DURATION;
};

/**
 * Get all categories
 * GET /api/categories/
 * 
 * Returns cached categories if available and not stale.
 * Otherwise, fetches from the API and updates the cache.
 * 
 * @returns Array of categories ordered by priority level (highest first)
 * @throws Error if fetching categories fails
 */
const getCategories = async (): Promise<Category[]> => {
  // Return cached data if valid
  if (isCacheValid() && categoryCache) {
    return categoryCache;
  }
  
  try {
    const response = await apiClient.get<Category[]>('/categories/');
    
    // Sort categories by priority level (highest first: 5 > 4 > 3 > 2 > 1)
    const sortedCategories = response.data.sort(
      (a, b) => b.priority_level - a.priority_level
    );
    
    // Update cache
    categoryCache = sortedCategories;
    cacheTimestamp = Date.now();
    
    return sortedCategories;
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Failed to fetch categories. Please try again.';
    throw new Error(errorMessage);
  }
};

/**
 * Get a single category by ID
 * GET /api/categories/{id}/
 * 
 * First checks the cache for the category. If not found or cache is stale,
 * fetches from the API.
 * 
 * @param id - The category ID
 * @returns Category object
 * @throws Error if fetching category fails
 */
const getCategory = async (id: number): Promise<Category> => {
  // Check cache first if valid
  if (isCacheValid() && categoryCache) {
    const cachedCategory = categoryCache.find(cat => cat.id === id);
    if (cachedCategory) {
      return cachedCategory;
    }
  }
  
  try {
    const response = await apiClient.get<Category>(`/categories/${id}/`);
    
    // Update cache with this category if cache exists
    if (categoryCache) {
      const existingIndex = categoryCache.findIndex(cat => cat.id === id);
      if (existingIndex >= 0) {
        categoryCache[existingIndex] = response.data;
      } else {
        categoryCache.push(response.data);
        // Re-sort after adding new category
        categoryCache.sort((a, b) => b.priority_level - a.priority_level);
      }
    }
    
    return response.data;
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Failed to fetch category. Please try again.';
    throw new Error(errorMessage);
  }
};

/**
 * Clear the category cache
 * Useful for forcing a refresh of category data
 */
export const clearCategoryCache = (): void => {
  categoryCache = null;
  cacheTimestamp = null;
};

/**
 * Export category service object implementing CategoryService interface
 */
const categoryService: CategoryService = {
  getCategories,
  getCategory,
};

export default categoryService;
