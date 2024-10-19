import React, { useEffect } from 'react';
import { signIn, useSession } from 'next-auth/react';
import { useRouter } from 'next/router';
import Layout from '@/components/layout';
import Button from '@/components/common/button';

const LoginPage: React.FC = () => {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (session) {
      router.push('/dashboard');
    }
  }, [session, router]);

  if (status === 'loading') {
    return (
      <Layout title="Loading | Education Platform">
        <div className="flex justify-center items-center h-screen">
          <p className="text-xl">Loading...</p>
        </div>
      </Layout>
    );
  }

  const handleGoogleSignIn = () => {
    signIn('google', { callbackUrl: '/dashboard' });
  };

  const handleEmailSignIn = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const email = (e.currentTarget.elements.namedItem('email') as HTMLInputElement).value;
    if (email) {
      signIn('email', { email, callbackUrl: '/dashboard' });
    }
  };

  return (
    <Layout title="Login | Education Platform">
      <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
        <h1 className="text-3xl font-bold mb-6 text-center">Login</h1>
        <Button
          onClick={handleGoogleSignIn}
          className="w-full mb-4 bg-red-500 hover:bg-red-600 text-white"
        >
          Sign in with Google
        </Button>
        <div className="relative my-6">
          <hr className="border-t border-gray-300" />
          <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white px-2 text-gray-500">
            or
          </span>
        </div>
        <form onSubmit={handleEmailSignIn}>
          <div className="mb-4">
            <label htmlFor="email" className="block text-gray-700 text-sm font-bold mb-2">
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
            />
          </div>
          <Button type="submit" className="w-full bg-blue-500 hover:bg-blue-600 text-white">
            Sign in with Email
          </Button>
        </form>
      </div>
    </Layout>
  );
};

export default LoginPage;
