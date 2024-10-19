import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import theme from '../styles/theme'
import Layout from '../components/layout'
import { SessionProvider } from "next-auth/react"
import { EthereumClient, w3mConnectors, w3mProvider } from '@web3modal/ethereum'
import { Web3Modal } from '@web3modal/react'
import { createConfig, WagmiConfig } from 'wagmi'
import { arbitrum, mainnet, polygon } from 'wagmi/chains'
import { AuthProvider } from '../context/auth-context';

const chains = [arbitrum, mainnet, polygon]
const projectId = process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID!

const wagmiConfig = createConfig({
  autoConnect: true,
  connectors: w3mConnectors({ projectId, chains }),
  provider: w3mProvider({ projectId }),
})

const ethereumClient = new EthereumClient(wagmiConfig, chains)

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <SessionProvider>
        <WagmiConfig config={wagmiConfig}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <Layout>
              <Component {...pageProps} />
            </Layout>
          </ThemeProvider>
        </WagmiConfig>
        <Web3Modal projectId={projectId} ethereumClient={ethereumClient} />
      </SessionProvider>
    </AuthProvider>
  )
}

export default MyApp
