import { FC } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { EvaluationResultCreate } from '@/lib/api';

const evaluationSchema = z.object({
  status: z.enum(['Needs Improvement', 'Satisfactory', 'Excellent']),
  criteria: z.array(
    z.object({
      name: z.string().min(1, 'Name is required'),
      score: z.number().min(0).max(5),
      rationale: z.string().min(1, 'Rationale is required'),
    })
  ),
  improvementSuggestion: z.string().optional(),
});

type EvaluationFormData = z.infer<typeof evaluationSchema>;

interface EvaluationFormProps {
  initialData?: EvaluationResultCreate;
  onSubmit: (data: EvaluationResultCreate) => void;
  isLoading?: boolean;
}

export const EvaluationForm: FC<EvaluationFormProps> = ({
  initialData,
  onSubmit,
  isLoading = false,
}) => {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<EvaluationFormData>({
    resolver: zodResolver(evaluationSchema),
    defaultValues: initialData || {
      status: 'Needs Improvement',
      criteria: [{ name: '', score: 0, rationale: '' }],
      improvementSuggestion: '',
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'criteria',
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Evaluation Status</h3>
        </CardHeader>
        <CardContent>
          <Select
            {...register('status')}
            onValueChange={(value) => {
              register('status').onChange({
                target: { value, name: 'status' },
              });
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Needs Improvement">Needs Improvement</SelectItem>
              <SelectItem value="Satisfactory">Satisfactory</SelectItem>
              <SelectItem value="Excellent">Excellent</SelectItem>
            </SelectContent>
          </Select>
          {errors.status && (
            <p className="text-sm text-red-500">{errors.status.message}</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Evaluation Criteria</h3>
            <Button
              type="button"
              variant="outline"
              onClick={() => append({ name: '', score: 0, rationale: '' })}
            >
              Add Criterion
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {fields.map((field, index) => (
              <div key={field.id} className="space-y-4 p-4 border rounded-lg">
                <div className="flex justify-between items-start gap-4">
                  <div className="flex-1">
                    <Input
                      {...register(`criteria.${index}.name`)}
                      placeholder="Criterion name"
                    />
                    {errors.criteria?.[index]?.name && (
                      <p className="text-sm text-red-500">
                        {errors.criteria[index]?.name?.message}
                      </p>
                    )}
                  </div>
                  <div className="w-24">
                    <Input
                      type="number"
                      {...register(`criteria.${index}.score`, {
                        valueAsNumber: true,
                      })}
                      placeholder="Score"
                    />
                    {errors.criteria?.[index]?.score && (
                      <p className="text-sm text-red-500">
                        {errors.criteria[index]?.score?.message}
                      </p>
                    )}
                  </div>
                  {fields.length > 1 && (
                    <Button
                      type="button"
                      variant="destructive"
                      onClick={() => remove(index)}
                    >
                      Remove
                    </Button>
                  )}
                </div>
                <Textarea
                  {...register(`criteria.${index}.rationale`)}
                  placeholder="Rationale"
                />
                {errors.criteria?.[index]?.rationale && (
                  <p className="text-sm text-red-500">
                    {errors.criteria[index]?.rationale?.message}
                  </p>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Improvement Suggestion</h3>
        </CardHeader>
        <CardContent>
          <Textarea
            {...register('improvementSuggestion')}
            placeholder="Enter improvement suggestions..."
          />
          {errors.improvementSuggestion && (
            <p className="text-sm text-red-500">
              {errors.improvementSuggestion.message}
            </p>
          )}
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Evaluation'}
        </Button>
      </div>
    </form>
  );
}; 