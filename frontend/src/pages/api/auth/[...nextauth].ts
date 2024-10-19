import NextAuth, { NextAuthOptions, Session, User } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import EmailProvider from "next-auth/providers/email"
import CredentialsProvider from "next-auth/providers/credentials"
import { JWT } from "next-auth/jwt"
import { verifyJWT } from "@/utils/auth"

interface ExtendedSession extends Session {
  accessToken?: string;
  user: {
    id?: string;
    name?: string | null;
    email?: string | null;
    image?: string | null;
    address?: string | null;
  };
}

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    EmailProvider({
      server: process.env.EMAIL_SERVER,
      from: process.env.EMAIL_FROM,
    }),
    CredentialsProvider({
      name: "Web3",
      credentials: {
        access_token: { label: "Access Token", type: "text" },
      },
      async authorize(credentials) {
        if (credentials?.access_token) {
          try {
            const user = await verifyJWT(credentials.access_token);
            return user;
          } catch (error) {
            console.error("Error verifying JWT:", error);
            return null;
          }
        }
        return null;
      },
    }),
  ],
  pages: {
    signIn: '/login',
  },
  callbacks: {
    async jwt({ token, user, account }) {
      if (account && user) {
        return {
          ...token,
          accessToken: account.access_token,
          address: (user as any).address,
        };
      }
      return token;
    },
    async session({ session, token }: { session: Session; token: JWT }): Promise<ExtendedSession> {
      const extendedSession = session as ExtendedSession;
      
      if (token.accessToken) {
        extendedSession.accessToken = token.accessToken as string;
      }
      if (token.sub) {
        extendedSession.user.id = token.sub;
      }
      if (token.address) {
        extendedSession.user.address = token.address as string;
      }

      return extendedSession;
    }
  },
  session: {
    strategy: 'jwt' as const,
  },
}

export default NextAuth(authOptions)
