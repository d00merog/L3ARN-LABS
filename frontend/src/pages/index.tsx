import React from 'react';
import Layout from '../components/layout';
import CourseList from '../components/course/course-list';
import { useAuth } from '../context/auth-context';
import Link from 'next/link';

const Home: React.FC = () => {
  const { user } = useAuth();

  return (
    <Layout title="Home | Education Platform">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-4">Welcome to our Education Platform</h1>
        <p className="text-xl mb-8">Empowering learning and language preservation</p>
        
        {user ? (
          <>
            <h2 className="text-2xl font-semibold mb-4">Your Courses</h2>
            <CourseList />
          </>
        ) : (
          <div className="mb-8">
            <p className="mb-4">Join our platform to start learning and preserving languages!</p>
            <Link href="/auth/signup" className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded mr-4">
              Sign Up
            </Link>
            <Link href="/auth/login" className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
              Log In
            </Link>
          </div>
        )}
        
        <section className="mt-12">
          <h2 className="text-2xl font-semibold mb-4">Featured Courses</h2>
          <CourseList featured={true} />
        </section>
      </div>
    </Layout>
  );
};

export default Home;