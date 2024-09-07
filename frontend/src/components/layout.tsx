import React, { ReactNode } from 'react';
import Head from 'next/head';

type LayoutProps = {
  children: ReactNode;
  title?: string;
};

const Layout: React.FC<LayoutProps> = ({ children, title = 'Education Platform' }) => {
  return (
    <div>
      <Head>
        <title>{title}</title>
        <meta charSet="utf-8" />
        <meta name="viewport" content="initial-scale=1.0, width=device-width" />
      </Head>
      <header>
        <nav>
          {/* Add navigation items here */}
        </nav>
      </header>
      <main>{children}</main>
      <footer>
        <hr />
        <span>Education Platform © 2023</span>
      </footer>
    </div>
  );
};

export default Layout;