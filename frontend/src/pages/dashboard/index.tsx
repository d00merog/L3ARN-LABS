import React from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import { useRouter } from 'next/router';
import DashboardOverview from '../../components/dashboard/overview/DashboardOverview';

const DashboardPage: NextPage = () => {
  const router = useRouter();

  return (
    <>
      <Head>
        <title>Dashboard - L3ARN Labs</title>
        <meta 
          name="description" 
          content="Your personalized learning dashboard with progress tracking, WebVM management, and Bittensor analytics."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <DashboardOverview />
    </>
  );
};

export default DashboardPage;