import React, { useState } from 'react';
// Import the creation context to auto-fill the form
// JS module provides runtime values; TS will infer `any` types.
// This enables us to set title, description, and questions after generation.
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { useCreateSurveyProvider } from './CreateSurveyProvider';

interface Scale {
  min: number;
  max: number;
  labels?: string[];
}

interface Question {
  id: string;
  type: string;
  text: string;
  required: boolean;
  options?: string[];
  scale?: Scale;
}

interface Survey {
  id: string;
  title: string;
  description: string;
  questions: Question[];
  createdAt: string;
}

const SurveyGenerator: React.FC = () => {
  const [description, setDescription] = useState('');
  const [survey, setSurvey] = useState<Survey | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const {
    setSurveyTitle,
    setSurveyDescription,
    setQuestions,
  } = useCreateSurveyProvider();

  const mapBackendTypeToUI = (t: string): string => {
    switch (t) {
      case 'multiple_choice':
        return 'singleChoice';
      case 'checkboxes':
        return 'multipleChoice';
      case 'open_text':
        return 'openQuestion';
      case 'rating':
      case 'likert':
        return 'scale';
      case 'yes_no':
        return 'singleChoice';
      case 'matrix':
        return 'multipleChoice';
      default:
        return 'shortAnswer';
    }
  };

  const toProviderQuestions = (qs: Question[]) => {
    const makeId = () => Date.now() + Math.random();

    return qs.map((q) => {
      const uiType = mapBackendTypeToUI(q.type);
      let options: Array<{ id: number; text: string }> = [];

      if (uiType === 'singleChoice' || uiType === 'multipleChoice') {
        if (q.type === 'yes_no') {
          options = [
            { id: makeId(), text: 'Yes' },
            { id: makeId(), text: 'No' },
          ];
        } else if (q.options && q.options.length) {
          options = q.options.map((opt) => ({ id: makeId(), text: opt }));
        } else {
          // Ensure minimum two options exist for choice questions
          options = [
            { id: makeId(), text: '' },
            { id: makeId(), text: '' },
          ];
        }
      }

      return {
        id: (q.id as unknown) as number | string,
        type: uiType,
        title: q.text,
        saved: false,
        options,
      } as unknown as any; // provider is JS, accept loose typing here
    });
  };

  const generate = async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await fetch('/api/surveys/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      if (!resp.ok) {
        throw new Error(`Error ${resp.status}`);
      }
      const data = (await resp.json()) as Survey;
      setSurvey(data);

      // Push into the creation form
      try {
        setSurveyTitle(data.title);
        setSurveyDescription(data.description);
        setQuestions(toProviderQuestions(data.questions));
      } catch (e) {
        // Non-fatal: keep showing the generated preview
        console.error('Failed to apply generated survey to form', e);
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="my-4">
      <div className="flex space-x-2">
        <input
          className="border p-2 flex-1"
          placeholder="Survey description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button
          className="bg-blue-600 text-white px-4 py-2"
          onClick={generate}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate Survey'}
        </button>
      </div>
      {error && <p className="text-red-500 mt-2">{error}</p>}
      {survey && (
        <div className="mt-4">
          <h3 className="text-xl font-bold">{survey.title}</h3>
          <p className="mb-2">{survey.description}</p>
          <ul className="list-disc ml-5">
            {survey.questions.map((q) => (
              <li key={q.id}>{q.text}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SurveyGenerator;
