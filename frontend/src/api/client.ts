import axios, { AxiosInstance, AxiosError } from 'axios';

// Type definitions
export interface Email {
  id: number;
  mailbox_id: number;
  message_id: string;
  from_address: string;
  to_address: string;
  subject: string;
  html_body: string;
  text_body: string;
  is_read: boolean;
  is_starred: boolean;
  folder: string;
  received_at: string;
  verification_link?: string;
}

export interface Mailbox {
  id: number;
  email: string;
  display_name?: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

// Error handling
class ApiError extends Error {
  constructor(public message: string, public statusCode?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ error?: string; message?: string }>;
    return (
      axiosError.response?.data?.error ||
      axiosError.response?.data?.message ||
      axiosError.message ||
      'An unexpected error occurred'
    );
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred';
}

// Axios instance configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = extractErrorMessage(error);
    const statusCode = axios.isAxiosError(error) ? error.response?.status : undefined;
    throw new ApiError(message, statusCode);
  }
);

// API methods
export const api = {
  /**
   * Get all mailboxes
   */
  async getMailboxes(): Promise<Mailbox[]> {
    const response = await apiClient.get<Mailbox[]>('/mailboxes');
    return response.data;
  },

  /**
   * Get emails with optional filtering and pagination
   */
  async getEmails(
    folder?: string,
    page: number = 1
  ): Promise<PaginatedResponse<Email>> {
    const params: Record<string, string | number> = { page };
    if (folder) {
      params.folder = folder;
    }
    const response = await apiClient.get<PaginatedResponse<Email>>('/emails', {
      params,
    });
    return response.data;
  },

  /**
   * Get a single email by ID
   */
  async getEmail(id: number): Promise<Email> {
    const response = await apiClient.get<Email>(`/emails/${id}`);
    return response.data;
  },

  /**
   * Update an email (mark as read, starred, change folder, etc.)
   */
  async updateEmail(id: number, updates: Partial<Email>): Promise<Email> {
    const response = await apiClient.put<Email>(`/emails/${id}`, updates);
    return response.data;
  },

  /**
   * Delete an email
   */
  async deleteEmail(id: number): Promise<void> {
    await apiClient.delete(`/emails/${id}`);
  },

  /**
   * Search emails by query string
   */
  async searchEmails(query: string): Promise<Email[]> {
    const response = await apiClient.get<Email[]>('/emails/search', {
      params: { q: query },
    });
    return response.data;
  },
};

export default api;
