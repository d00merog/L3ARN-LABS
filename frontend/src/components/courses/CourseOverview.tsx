import React, { useState } from 'react';
import { Typography, Box, Stepper, Step, StepLabel, StepContent, Button, Paper } from '@mui/material';
import { Course, Lesson } from '@/types/course';

interface CourseOverviewProps {
  course: Course;
  lessons: Lesson[];
  onStartCourse: () => void;
}

const CourseOverview: React.FC<CourseOverviewProps> = ({ course, lessons, onStartCourse }) => {
  const [activeStep, setActiveStep] = useState(0);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
  };

  return (
    <Box sx={{ maxWidth: 800, margin: 'auto' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {course.title}
      </Typography>
      <Typography variant="body1" paragraph>
        {course.description}
      </Typography>
      <Stepper activeStep={activeStep} orientation="vertical">
        {lessons.map((lesson, index) => (
          <Step key={lesson.id}>
            <StepLabel
              optional={
                index === lessons.length - 1 ? (
                  <Typography variant="caption">Last lesson</Typography>
                ) : null
              }
            >
              {lesson.title}
            </StepLabel>
            <StepContent>
              <Typography>{lesson.description}</Typography>
              <Box sx={{ mb: 2 }}>
                <div>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    {index === lessons.length - 1 ? 'Finish' : 'Continue'}
                  </Button>
                  <Button
                    disabled={index === 0}
                    onClick={handleBack}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    Back
                  </Button>
                </div>
              </Box>
            </StepContent>
          </Step>
        ))}
      </Stepper>
      {activeStep === lessons.length && (
        <Paper square elevation={0} sx={{ p: 3 }}>
          <Typography>All lessons completed - you&apos;re finished</Typography>
          <Button onClick={handleReset} sx={{ mt: 1, mr: 1 }}>
            Reset
          </Button>
          <Button onClick={onStartCourse} variant="contained" sx={{ mt: 1, mr: 1 }}>
            Start Course
          </Button>
        </Paper>
      )}
    </Box>
  );
};

export default CourseOverview;
