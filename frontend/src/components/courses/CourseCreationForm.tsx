import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { createCourse } from '../../api/courses';
import Button from '../common/button';

type CourseFormData = {
  title: string;
  description: string;
  type: 'language' | 'history';
  topic: string;
  difficulty?: string;
  era?: string;
  model: string;
};

const CourseCreationForm: React.FC = () => {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<CourseFormData>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const courseType = watch('type');

  const onSubmit = async (data: CourseFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      await createCourse(data);
      // Handle success (e.g., show a success message, redirect)
    } catch (error) {
      setError('Failed to create course. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <input {...register('title', { required: 'Title is required' })} placeholder="Course Title" className="w-full p-2 border rounded" />
      {errors.title && <span className="text-red-500">{errors.title.message}</span>}
      
      <textarea {...register('description', { required: 'Description is required' })} placeholder="Course Description" className="w-full p-2 border rounded" />
      {errors.description && <span className="text-red-500">{errors.description.message}</span>}
      
      <select {...register('type', { required: 'Type is required' })} className="w-full p-2 border rounded">
        <option value="">Select Type</option>
        <option value="language">Language</option>
        <option value="history">History</option>
      </select>
      {errors.type && <span className="text-red-500">{errors.type.message}</span>}
      
      <input {...register('topic', { required: 'Topic is required' })} placeholder="Topic" className="w-full p-2 border rounded" />
      {errors.topic && <span className="text-red-500">{errors.topic.message}</span>}
      
      {courseType === 'language' && (
        <select {...register('difficulty', { required: 'Difficulty is required for language courses' })} className="w-full p-2 border rounded">
          <option value="">Select Difficulty</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      )}
      {errors.difficulty && <span className="text-red-500">{errors.difficulty.message}</span>}
      
      {courseType === 'history' && (
        <input {...register('era', { required: 'Era is required for history courses' })} placeholder="Historical Era" className="w-full p-2 border rounded" />
      )}
      {errors.era && <span className="text-red-500">{errors.era.message}</span>}
      
      <select {...register('model', { required: 'Model is required' })} className="w-full p-2 border rounded">
        <option value="">Select Model</option>
        <option value="claude">Claude</option>
        <option value="openai">OpenAI</option>
        <option value="huggingface">HuggingFace</option>
        <option value="local">Local Model</option>
      </select>
      {errors.model && <span className="text-red-500">{errors.model.message}</span>}
      
      {error && <div className="text-red-500">{error}</div>}
      
      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? 'Creating...' : 'Create Course'}
      </Button>
    </form>
  );
};

export default CourseCreationForm;
