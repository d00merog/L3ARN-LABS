import React from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import WebVMDashboard from '../../components/dashboard/webvm/WebVMDashboard';

const WebVMDashboardPage: NextPage = () => {
  return (
    <>
      <Head>
        <title>WebVM Dashboard - L3ARN Labs</title>
        <meta 
          name="description" 
          content="Manage your browser-based virtual machines, execute code, and collaborate in real-time."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <WebVMDashboard />
    </>
  );
};

export default WebVMDashboardPage;