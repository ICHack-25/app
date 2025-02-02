import NextAuth from 'next-auth';

export const { handlers, signIn, signOut, useSession } = NextAuth( {
    providers: [],
})
