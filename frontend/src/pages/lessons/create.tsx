import React from 'react'
import Layout from '@/components/layout'
import LessonEditor from '@/components/lessons/LessonEditor'
import { Typography, Box } from '@mui/material'

const CreateLessonPage: React.FC = () => {
  const courseId = 1 // placeholder course ID
  return (
    <Layout title="Create Lesson | AI-Powered Learning Platform">
      <Box maxWidth={800} margin="auto">
        <Typography variant="h3" component="h1" gutterBottom>
          New Lesson
        </Typography>
        <LessonEditor courseId={courseId} />
      </Box>
    </Layout>
  )
}

export default CreateLessonPage
