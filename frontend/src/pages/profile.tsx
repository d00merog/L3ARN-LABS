import React, { useState, useEffect } from 'react';
import Layout from '@/components/layout';
import { useAuth } from '@/context/auth-context';
import api from '@/utils/api';
import Button from '@/components/common/button';

interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name: string;
}

const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedProfile, setEditedProfile] = useState<Partial<UserProfile>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      if (user?.id) {
        try {
          const response = await api.get<UserProfile>(`/users/${user.id}`);
          setProfile(response.data);
        } catch (error) {
          setError('Error fetching user profile. Please try again later.');
        } finally {
          setIsLoading(false);
        }
      } else {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [user]);

  const handleEdit = () => {
    setIsEditing(true);
    setEditedProfile({ ...profile });
  };

  const handleSave = async () => {
    if (!user?.id) return;

    try {
      const response = await api.put<UserProfile>(`/users/${user.id}`, editedProfile);
      setProfile(response.data);
      setIsEditing(false);
      setError(null);
    } catch (error) {
      setError('Error updating user profile. Please try again.');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setEditedProfile((prev: Partial<UserProfile>) => ({ ...prev, [name]: value }));
  };

  if (isLoading) {
    return <Layout title="Profile | Education Platform"><div>Loading profile...</div></Layout>;
  }

  if (error) {
    return <Layout title="Profile | Education Platform"><div className="text-red-500">{error}</div></Layout>;
  }

  if (!profile) {
    return <Layout title="Profile | Education Platform"><div>No profile data available.</div></Layout>;
  }

  return (
    <Layout title="Profile | Education Platform">
      <h1 className="text-3xl font-bold mb-6">User Profile</h1>
      <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
        {isEditing ? (
          <>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                Username
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="username"
                type="text"
                name="username"
                value={editedProfile.username || ''}
                onChange={handleChange}
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
                Email
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="email"
                type="email"
                name="email"
                value={editedProfile.email || ''}
                onChange={handleChange}
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="full_name">
                Full Name
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="full_name"
                type="text"
                name="full_name"
                value={editedProfile.full_name || ''}
                onChange={handleChange}
              />
            </div>
            <Button onClick={handleSave}>Save</Button>
          </>
        ) : (
          <>
            <p className="mb-2"><strong>Username:</strong> {profile.username}</p>
            <p className="mb-2"><strong>Email:</strong> {profile.email}</p>
            <p className="mb-2"><strong>Full Name:</strong> {profile.full_name}</p>
            <Button onClick={handleEdit}>Edit Profile</Button>
          </>
        )}
      </div>
    </Layout>
  );
};

export default ProfilePage;
