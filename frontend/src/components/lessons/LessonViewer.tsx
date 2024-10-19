import React from 'react'
import { Box, Typography, Paper } from '@mui/material'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { materialDark } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import { Components } from 'react-markdown'

interface LessonViewerProps {
  lesson: {
    title: string
    content: string
  }
}

const LessonViewer: React.FC<LessonViewerProps> = ({ lesson }) => {
  const components: Components = {
    code({ inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '')
      if (!inline && match) {
        // Destructure and omit 'ref' from props
        const { ref, ...restProps } = props
        return (
          <SyntaxHighlighter
            style={materialDark}
            language={match[1]}
            PreTag="div"
            {...restProps}
          >
            {String(children).replace(/\n$/, '')}
          </SyntaxHighlighter>
        )
      } else {
        return (
          <code className={className} {...props}>
            {children}
          </code>
        )
      }
    },
  }

  return (
    <Paper elevation={3} sx={{ p: 3, my: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {lesson.title}
      </Typography>
      <Box sx={{ mt: 2 }}>
        <ReactMarkdown components={components}>
          {lesson.content}
        </ReactMarkdown>
      </Box>
    </Paper>
  )
}

export default LessonViewer
