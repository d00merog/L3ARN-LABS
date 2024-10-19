import NextAuth, { NextAuthOptions, Session, User } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import EmailProvider from "next-auth/providers/email"
import { JWT } from "next-auth/jwt"

interface ExtendedSession extends Session {
  accessToken?: string;
  user: {
    id?: string;
    name?: string | null;
    email?: string | null;
    image?: string | null;
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
  ],
  pages: {
    signIn: '/login',
  },
  callbacks: {
    async session({ session, token, user }: { session: Session; token: JWT; user: User }): Promise<ExtendedSession> {
      const extendedSession = session as ExtendedSession;
      
      if (token.accessToken) {
        extendedSession.accessToken = token.accessToken as string;
      }
      if (token.sub) {
        extendedSession.user.id = token.sub;
      }

      return extendedSession;
    }
  },
  session: {
    strategy: 'jwt' as const,
  },
}

export default NextAuth(authOptions)
