import React from 'react'
import { Typography, Paper, Box } from '@mui/material'
import { Lesson } from '@/types/course'

interface LessonViewerProps {
  lesson: Lesson
}

const LessonViewer: React.FC<LessonViewerProps> = ({ lesson }) => {
  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h4" component="h2" gutterBottom>
        {lesson.title}
      </Typography>
      <Box dangerouslySetInnerHTML={{ __html: lesson.content }} />
    </Paper>
  )
}

export default LessonViewer
