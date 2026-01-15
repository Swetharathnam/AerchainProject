import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';

const formSchema = z.object({
    naturalLanguage: z.string().min(10, "Please describe your request in more detail."),
});

export function RFPForm() {
    const [isLoading, setIsLoading] = useState(false);
    const [structuredData, setStructuredData] = useState<any>(null);

    const { register, handleSubmit, formState: { errors } } = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
    });

    const onSubmit = async (data: z.infer<typeof formSchema>) => {
        setIsLoading(true);
        try {
            const result = await api.generateRFPStructure(data.naturalLanguage);
            setStructuredData(result);
        } catch (error) {
            console.error("Failed to generate RFP", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSave = async () => {
        if (!structuredData) return;
        try {
            await api.createRFP({
                title: structuredData.title,
                description: structuredData.description, // Use AI description or original input
                budget: structuredData.budget,
                currency: structuredData.currency,
                structured_data: JSON.stringify(structuredData) // Convert to JSON string
            });
            alert("RFP Saved Successfully!");
            setStructuredData(null); // Reset
        } catch (error) {
            console.error("Failed to save RFP", error);
            alert("Failed to save RFP");
        }
    };

    return (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2">
            <Card>
                <CardHeader>
                    <CardTitle>Create New RFP</CardTitle>
                    <CardDescription>Describe what you need to procure in plain English.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="naturalLanguage">Requirement Description</Label>
                            <Textarea
                                id="naturalLanguage"
                                placeholder="E.g. I need 50 high-end laptops for our design team, delivered by next month..."
                                className="min-h-[200px]"
                                {...register("naturalLanguage")}
                            />
                            {errors.naturalLanguage && (
                                <p className="text-sm text-red-500">{errors.naturalLanguage.message}</p>
                            )}
                        </div>
                        <Button type="submit" disabled={isLoading} className="w-full">
                            {isLoading ? "Analyzing with AI..." : "Generate RFP Structure"}
                        </Button>
                    </form>
                </CardContent>
            </Card>

            {structuredData && (
                <Card className={`border-2 ${structuredData.error ? 'border-amber-200 bg-amber-50/50' : 'border-green-200 bg-green-50/50'} dark:bg-opacity-10`}>
                    <CardHeader>
                        <CardTitle className="flex justify-between items-center">
                            AI Suggested Structure
                            {structuredData.error && <span className="text-xs bg-amber-200 text-amber-800 px-2 py-1 rounded">AI Unavailable</span>}
                        </CardTitle>
                        <CardDescription>
                            {structuredData.error
                                ? "We couldn't reach the AI (Rate Limit). You can still edit and save manually below."
                                : "Review the extracted details before saving."}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {structuredData.error && (
                            <div className="p-3 bg-white border border-amber-200 rounded text-xs text-amber-700 font-mono mb-4">
                                Error: {structuredData.error.includes("429") ? "Rate limit reached. Please wait a moment." : structuredData.error}
                            </div>
                        )}
                        <div className="grid gap-2">
                            <Label>Title</Label>
                            <Input
                                value={structuredData.title}
                                onChange={(e) => setStructuredData({ ...structuredData, title: e.target.value })}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label>Summary Description</Label>
                            <Textarea
                                value={structuredData.description}
                                className="min-h-[100px]"
                                onChange={(e) => setStructuredData({ ...structuredData, description: e.target.value })}
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="grid gap-2">
                                <Label>Budget</Label>
                                <Input
                                    value={structuredData.budget || ""}
                                    placeholder="N/A"
                                    onChange={(e) => setStructuredData({ ...structuredData, budget: e.target.value })}
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label>Currency</Label>
                                <Input
                                    value={structuredData.currency || "USD"}
                                    onChange={(e) => setStructuredData({ ...structuredData, currency: e.target.value })}
                                />
                            </div>
                        </div>

                        {structuredData.requirements && structuredData.requirements.length > 0 && (
                            <div className="grid gap-2">
                                <Label>Key Requirements</Label>
                                <ul className="list-disc pl-5 text-sm">
                                    {structuredData.requirements.map((req: string, i: number) => (
                                        <li key={i}>{req}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </CardContent>
                    <CardFooter>
                        <Button onClick={handleSave} className={`w-full ${structuredData.error ? 'bg-amber-600 hover:bg-amber-700' : 'bg-green-600 hover:bg-green-700'}`}>
                            {structuredData.error ? "Save Manual RFP" : "Confirm & Save RFP"}
                        </Button>
                    </CardFooter>
                </Card>
            )}
        </div>
    );
}
