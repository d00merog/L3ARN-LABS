import React from 'react'
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material'
import Link from 'next/link'
import { useSession, signOut } from "next-auth/react"

const Navbar: React.FC = () => {
  const { data: session } = useSession()

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          <Link href="/" passHref>
            <Button color="inherit">Education Platform</Button>
          </Link>
        </Typography>
        <Box>
          <Link href="/courses" passHref>
            <Button color="inherit">Courses</Button>
          </Link>
          {session ? (
            <>
              <Link href="/dashboard" passHref>
                <Button color="inherit">Dashboard</Button>
              </Link>
              <Button color="inherit" onClick={() => signOut()}>Logout</Button>
            </>
          ) : (
            <Link href="/login" passHref>
              <Button color="inherit">Login</Button>
            </Link>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar
