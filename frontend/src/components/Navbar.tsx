import React from 'react'
import { AppBar, Toolbar, Typography, Button, Box, Avatar, Menu, MenuItem, IconButton } from '@mui/material'
import Link from 'next/link'
import { useSession, signOut } from "next-auth/react"
import { useRouter } from 'next/router'
import MenuIcon from '@mui/icons-material/Menu'

const Navbar: React.FC = () => {
  const { data: session } = useSession()
  const router = useRouter()
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null)
  const [mobileMenuAnchorEl, setMobileMenuAnchorEl] = React.useState<null | HTMLElement>(null)

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMobileMenu = (event: React.MouseEvent<HTMLElement>) => {
    setMobileMenuAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
    setMobileMenuAnchorEl(null)
  }

  const handleSignOut = () => {
    signOut()
    handleClose()
  }

  const menuItems = [
    { label: 'Courses', path: '/courses' },
    { label: 'Language Preservation', path: '/language-preservation' },
    { label: 'Dashboard', path: '/dashboard', authRequired: true },
    { label: 'Instructor Dashboard', path: '/instructor-dashboard', authRequired: true },
  ]

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          <Link href="/" passHref>
            <Button color="inherit">AI-Powered Learning Platform</Button>
          </Link>
        </Typography>
        <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
          {menuItems.map((item) => (
            (!item.authRequired || session) && (
              <Button key={item.label} color="inherit" onClick={() => router.push(item.path)}>
                {item.label}
              </Button>
            )
          ))}
          {session ? (
            <>
              <Avatar
                alt={session.user?.name || ''}
                src={session.user?.image || ''}
                onClick={handleMenu}
                sx={{ cursor: 'pointer', ml: 2 }}
              />
              <Menu
                id="menu-appbar"
                anchorEl={anchorEl}
                anchorOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                open={Boolean(anchorEl)}
                onClose={handleClose}
              >
                <MenuItem onClick={() => { router.push('/profile'); handleClose(); }}>Profile</MenuItem>
                <MenuItem onClick={handleSignOut}>Logout</MenuItem>
              </Menu>
            </>
          ) : (
            <Button color="inherit" onClick={() => router.push('/login')}>Login</Button>
          )}
        </Box>
        <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
          <IconButton
            size="large"
            aria-label="show more"
            aria-controls="menu-mobile"
            aria-haspopup="true"
            onClick={handleMobileMenu}
            color="inherit"
          >
            <MenuIcon />
          </IconButton>
          <Menu
            id="menu-mobile"
            anchorEl={mobileMenuAnchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(mobileMenuAnchorEl)}
            onClose={handleClose}
          >
            {menuItems.map((item) => (
              (!item.authRequired || session) && (
                <MenuItem key={item.label} onClick={() => { router.push(item.path); handleClose(); }}>
                  {item.label}
                </MenuItem>
              )
            ))}
            {session ? (
              <MenuItem onClick={handleSignOut}>Logout</MenuItem>
            ) : (
              <MenuItem onClick={() => { router.push('/login'); handleClose(); }}>Login</MenuItem>
            )}
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar
