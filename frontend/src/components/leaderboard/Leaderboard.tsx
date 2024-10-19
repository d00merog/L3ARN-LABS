import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from '@mui/material';

interface LeaderboardEntry {
  rank: number;
  username: string;
  xp: number;
  level: number;
}

interface LeaderboardProps {
  entries: LeaderboardEntry[];
}

const Leaderboard: React.FC<LeaderboardProps> = ({ entries }) => {
  return (
    <TableContainer component={Paper}>
      <Typography variant="h5" gutterBottom sx={{ p: 2 }}>
        Leaderboard
      </Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Rank</TableCell>
            <TableCell>Username</TableCell>
            <TableCell align="right">XP</TableCell>
            <TableCell align="right">Level</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {entries.map((entry) => (
            <TableRow key={entry.rank}>
              <TableCell component="th" scope="row">
                {entry.rank}
              </TableCell>
              <TableCell>{entry.username}</TableCell>
              <TableCell align="right">{entry.xp}</TableCell>
              <TableCell align="right">{entry.level}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default Leaderboard;
