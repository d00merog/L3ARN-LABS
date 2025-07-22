import React from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import HeroSection from '../components/landing/hero/HeroSection';
import FeaturesSection from '../components/landing/features/FeaturesSection';

const LandingPage: NextPage = () => {
  return (
    <>
      <Head>
        <title>L3ARN Labs - Revolutionary AI Education Platform</title>
        <meta 
          name="description" 
          content="The future of AI education powered by Bittensor, WebVM, and decentralized learning. Experience browser-based coding environments, AI tutors, and earn TAO tokens."
        />
        <meta name="keywords" content="AI education, Bittensor, WebVM, blockchain learning, TAO tokens, WebAssembly, decentralized education" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        
        {/* Open Graph meta tags */}
        <meta property="og:title" content="L3ARN Labs - Revolutionary AI Education Platform" />
        <meta property="og:description" content="Experience the future of education with AI tutors, browser coding, and blockchain rewards." />
        <meta property="og:type" content="website" />
        <meta property="og:image" content="/og-image.png" />
        
        {/* Twitter Card meta tags */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="L3ARN Labs - Revolutionary AI Education" />
        <meta name="twitter:description" content="AI-powered learning with Bittensor, WebVM, and TAO rewards." />
        <meta name="twitter:image" content="/twitter-image.png" />
      </Head>

      <main className="min-h-screen">
        <HeroSection />
        <FeaturesSection />
        
        {/* Additional sections would go here */}
        {/* <TestimonialsSection />
        <PricingSection />
        <CTASection /> */}
      </main>
    </>
  );
};

export default LandingPage;