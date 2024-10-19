import React from 'react';
import Link from 'next/link';
import { useSession, signOut } from 'next-auth/react';

declare module 'react' {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

const Navigation: React.FC = () => {
  const { data: session } = useSession();

  return (
    <nav className="bg-blue-600 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-white text-2xl font-bold">
          Education Platform
        </Link>
        <div className="space-x-4">
          <Link href="/courses" className="text-white hover:text-blue-200">
            Courses
          </Link>
          <Link href="/language-preservation" className="text-white hover:text-blue-200">
            Language Preservation
          </Link>
          {session ? (
            <>
              <Link href="/profile" className="text-white hover:text-blue-200">
                Profile
              </Link>
              <button onClick={() => signOut()} className="text-white hover:text-blue-200">
                Logout
              </button>
            </>
          ) : (
            <Link href="/login" className="text-white hover:text-blue-200">
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
