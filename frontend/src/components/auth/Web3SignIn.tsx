import React, { useState } from 'react';
import { useAccount, useConnect, useSignMessage, useDisconnect } from 'wagmi';
import { InjectedConnector } from 'wagmi/dist/connectors/injected';
import { Button, CircularProgress, Typography } from '@mui/material';
import { useRouter } from 'next/router';
import { getWeb3Nonce, verifyWeb3Signature } from '@/utils/api';
import { signIn } from 'next-auth/react';

const Web3SignIn: React.FC = () => {
  const { connectAsync } = useConnect();
  const { disconnectAsync } = useDisconnect();
  const { isConnected } = useAccount();
  const { signMessageAsync } = useSignMessage();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAuth = async () => {
    if (isConnected) {
      await disconnectAsync();
    }

    setIsLoading(true);
    setError(null);

    try {
      const connectResult = await connectAsync({ connector: new InjectedConnector() });
      const account = connectResult.accounts[0];
      const chain = connectResult.chainId;

      if (!account || !chain) {
        throw new Error('Failed to connect to wallet');
      }

      const userData = { address: account, chain: chain, network: 'evm' };

      const { message } = await getWeb3Nonce(userData.address, userData.chain, userData.network);

      const signature = await signMessageAsync({ message });

      const { access_token } = await verifyWeb3Signature(message, signature, userData.address, userData.chain, userData.network);

      const signInResult = await signIn('credentials', {
        redirect: false,
        access_token,
      });

      if (signInResult?.error) {
        setError(signInResult.error);
      } else {
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Error during Web3 authentication:', error);
      setError('Failed to authenticate. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Button
        onClick={handleAuth}
        variant="contained"
        color="secondary"
        fullWidth
        disabled={isLoading}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Sign In with Web3'}
      </Button>
      {error && (
        <Typography color="error" align="center" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}
    </>
  );
};

export default Web3SignIn;
