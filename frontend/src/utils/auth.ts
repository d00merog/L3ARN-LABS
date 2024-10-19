// Update API endpoints if needed
const API_URL = '/api/users';  // Adjust this if the endpoint has changed

export const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token')
  }
  return null
}

export const verifyJWT = async (token: string) => {
  try {
    // Instead of verifying the JWT on the client-side, we should send it to the server for verification
    const response = await fetch(`${API_URL}/verify-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });

    if (!response.ok) {
      throw new Error('Token verification failed');
    }

    const data = await response.json();
    return data.decoded;
  } catch (error) {
    console.error("Error verifying JWT:", error);
    throw error;
  }
};

// Update any API calls to match the new backend structure



