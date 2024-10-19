import React from 'react';
import Head from 'next/head';
import Layout from '../components/layout';
import LanguageInput from '../components/language-preservation/LanguageInput';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

const LanguagePreservationPage: React.FC = () => {
  const { data: session, status } = useSession();
  const router = useRouter();

  React.useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    }
  }, [status, router]);

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  return (
    <Layout>
      <Head>
        <title>Language Preservation | Education Platform</title>
        <meta name="description" content="Contribute to preserving endangered languages through text and audio samples" />
      </Head>
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Language Preservation</h1>
        <p className="mb-4">
          Help preserve endangered languages by contributing text and audio samples. Your contributions are valuable in our efforts to document and revitalize these languages.
        </p>
        <LanguageInput />
      </main>
    </Layout>
  );
};

export default LanguagePreservationPage;
