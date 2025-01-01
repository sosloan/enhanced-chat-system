import { FC } from 'react';
import { TranscriptionDetails as ITranscriptionDetails, EvaluationResult } from '@/types/transcription';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronLeft } from 'lucide-react';

interface TranscriptionEvaluationProps {
  details: ITranscriptionDetails;
  evaluationResults: EvaluationResult[];
  onBack: () => void;
}

export const TranscriptionEvaluation: FC<TranscriptionEvaluationProps> = ({
  details,
  evaluationResults,
  onBack,
}) => {
  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="mb-4 flex items-center justify-between">
        <Button 
          variant="ghost" 
          onClick={onBack}
          className="flex items-center gap-2"
        >
          <ChevronLeft className="h-4 w-4" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Evaluate Transcription</h1>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <h2 className="text-xl font-semibold">
            Transcription Details - {details.id}
          </h2>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Successful Call</p>
              <p>{details.successfulCall ? 'Yes' : 'No'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Classification</p>
              <p>{details.classification}</p>
            </div>
            <div className="col-span-2">
              <p className="text-sm text-gray-500">Filename</p>
              <p>{details.filename}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-6">
        {evaluationResults.map((result) => (
          <EvaluationResultCard key={result.id} result={result} />
        ))}
      </div>
    </div>
  );
};

interface EvaluationResultCardProps {
  result: EvaluationResult;
}

const EvaluationResultCard: FC<EvaluationResultCardProps> = ({ result }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Needs Improvement':
        return 'text-red-500';
      case 'Satisfactory':
        return 'text-yellow-500';
      case 'Excellent':
        return 'text-green-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold flex items-center gap-2">
          Evaluation {result.id}
          <span className={getStatusColor(result.status)}>
            ({result.status})
          </span>
        </h3>
      </CardHeader>
      <CardContent>
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Criteria</th>
              <th className="text-left py-2">Score</th>
              <th className="text-left py-2">Rationale</th>
            </tr>
          </thead>
          <tbody>
            {result.criteria.map((criterion, index) => (
              <tr key={index} className="border-b last:border-b-0">
                <td className="py-2">{criterion.name}</td>
                <td className="py-2">{criterion.score}</td>
                <td className="py-2">{criterion.rationale}</td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {result.improvementSuggestion && (
          <div className="mt-4">
            <p className="font-semibold">Improvement Suggestion:</p>
            <p className="text-gray-600">{result.improvementSuggestion}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}; 