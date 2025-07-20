import React, { useState } from 'react'
import { Box, Button, TextField } from '@mui/material'
import { createLesson } from '@/api/lessons'
import { Lesson } from '@/types/course'

interface LessonEditorProps {
  courseId: number
}

const LessonEditor: React.FC<LessonEditorProps> = ({ courseId }) => {
  const [content, setContent] = useState('')
  const [title, setTitle] = useState('')

  const handleSave = async () => {
    const lessonData: Omit<Lesson, 'id'> = {
      title,
      description: '',
      content,
      order: 1,
      difficulty: 'easy',
      course_id: courseId,
    }
    await createLesson(lessonData)
  }

  return (
    <Box display="flex" flexDirection="column" gap={2}>
      <TextField label="Title" value={title} onChange={e => setTitle(e.target.value)} fullWidth />
      <TextField
        label="Content (Markdown)"
        value={content}
        onChange={e => setContent(e.target.value)}
        fullWidth
        multiline
        rows={10}
      />
      <Button variant="contained" onClick={handleSave}>Save</Button>
    </Box>
  )
}

export default LessonEditor
