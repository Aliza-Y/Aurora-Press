const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchAPI(endpoint: string, options: RequestInit = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
        credentials: 'include',
    });

    if (!response.ok) {
        throw new Error(`API call failed: ${response.statusText}`);
    }

    return response.json();
}

export const api = {
    get: (endpoint: string) => fetchAPI(endpoint),
    post: (endpoint: string, data: any) => fetchAPI(endpoint, {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    put: (endpoint: string, data: any) => fetchAPI(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),
    delete: (endpoint: string) => fetchAPI(endpoint, {
        method: 'DELETE',
    }),
}; 