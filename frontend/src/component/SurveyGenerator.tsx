import React, { useState } from 'react';

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
