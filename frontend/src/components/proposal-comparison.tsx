import { useState, useEffect } from 'react';
import { api, type RFP } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

export function ProposalComparison() {
    const [rfps, setRfps] = useState<RFP[]>([]);
    const [vendors, setVendors] = useState<any[]>([]);
    const [selectedRfpId, setSelectedRfpId] = useState<string>("");
    const [proposals, setProposals] = useState<any[]>([]);

    // Form State
    const [selectedVendorId, setSelectedVendorId] = useState<string>("");
    const [proposalText, setProposalText] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        loadInitialData();
    }, []);

    useEffect(() => {
        if (selectedRfpId) {
            loadProposals(parseInt(selectedRfpId));
        } else {
            setProposals([]);
        }
    }, [selectedRfpId]);

    const loadInitialData = async () => {
        const [rfpData, vendorData] = await Promise.all([
            api.listRFPs(),
            api.listVendors()
        ]);
        setRfps(rfpData);
        setVendors(vendorData);
    };

    const loadProposals = async (rfpId: number) => {
        try {
            const data = await api.listProposals(rfpId);
            setProposals(data);
        } catch (error) {
            console.error("Failed to load proposals", error);
        }
    };

    const handleSubmitProposal = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedRfpId || !selectedVendorId || !proposalText) return;

        setIsSubmitting(true);
        try {
            await api.submitProposal({
                rfp_id: parseInt(selectedRfpId),
                vendor_id: parseInt(selectedVendorId),
                raw_response: proposalText
            });
            alert("Proposal submitted & Analyzed!");
            setProposalText("");
            loadProposals(parseInt(selectedRfpId)); // Refresh
        } catch (error) {
            console.error("Failed to submit proposal", error);
            alert("Failed to submit proposal");
        } finally {
            setIsSubmitting(false);
        }
    };

    // Helper to parse stored JSON safely
    const parseAnalysis = (jsonStr: string) => {
        try {
            return JSON.parse(jsonStr);
        } catch {
            return {};
        }
    };

    const [comparisonResult, setComparisonResult] = useState<any>(null);
    const [isComparing, setIsComparing] = useState(false);

    const handleCompareProposals = async () => {
        if (!selectedRfpId) return;
        setIsComparing(true);
        try {
            const result = await api.compareProposals(parseInt(selectedRfpId));
            setComparisonResult(result);
        } catch (error) {
            console.error("Failed to compare proposals", error);
            alert("Failed to compare proposals");
        } finally {
            setIsComparing(false);
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex flex-col space-y-4 md:flex-row md:space-x-4 md:space-y-0">
                <div className="w-full md:w-1/3 space-y-2">
                    <Label>Select RFP to Compare</Label>
                    <select
                        className="flex h-10 w-full items-center justify-between rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-950 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-zinc-800 dark:bg-zinc-950 dark:ring-offset-zinc-950 dark:placeholder:text-zinc-400 dark:focus:ring-zinc-300"
                        value={selectedRfpId}
                        onChange={(e) => {
                            setSelectedRfpId(e.target.value);
                            setComparisonResult(null); // Reset comparison when changing RFP
                        }}
                    >
                        <option value="">-- Select RFP --</option>
                        {rfps.map(r => (
                            <option key={r.id} value={r.id}>{r.title}</option>
                        ))}
                    </select>
                </div>
            </div>

            {selectedRfpId && (
                <div className="grid gap-6 lg:grid-cols-3">
                    {/* Input Column */}
                    <Card className="lg:col-span-1">
                        <CardHeader>
                            <CardTitle>Simulate Vendor Response</CardTitle>
                            <CardDescription>Paste a proposal text to trigger AI analysis.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={handleSubmitProposal} className="space-y-4">
                                <div className="space-y-2">
                                    <Label>Select Vendor</Label>
                                    <select
                                        className="flex h-10 w-full rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm"
                                        value={selectedVendorId}
                                        onChange={(e) => setSelectedVendorId(e.target.value)}
                                        required
                                    >
                                        <option value="">-- Vendor --</option>
                                        {vendors.map(v => (
                                            <option key={v.id} value={v.id}>{v.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <Label>Proposal Text</Label>
                                    <Textarea
                                        placeholder="Paste email or document text here... e.g. 'We can supply 10 units at $500 each...'"
                                        className="min-h-[200px]"
                                        value={proposalText}
                                        onChange={(e) => setProposalText(e.target.value)}
                                        required
                                    />
                                </div>
                                <Button type="submit" disabled={isSubmitting} className="w-full">
                                    {isSubmitting ? "Analyzing..." : "Submit & Analyze"}
                                </Button>
                            </form>
                        </CardContent>
                    </Card>

                    {/* Comparison Column */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Comparison Result Section */}
                        {proposals.length > 1 && (
                            <Card className="bg-slate-50 dark:bg-slate-900 border-2 border-primary/20">
                                <CardHeader>
                                    <CardTitle className="flex justify-between items-center">
                                        <span>Multi-Vendor Comparison</span>
                                        <Button
                                            onClick={handleCompareProposals}
                                            disabled={isComparing}
                                            variant="secondary"
                                        >
                                            {isComparing ? "Comparing..." : "Compare All Proposals"}
                                        </Button>
                                    </CardTitle>
                                    <CardDescription>Get an AI-generated ranking and recommendation.</CardDescription>
                                </CardHeader>
                                {comparisonResult && (
                                    <CardContent>
                                        <div className="space-y-4">
                                            <div className="p-4 bg-green-100 dark:bg-green-900/30 rounded-lg border border-green-200 dark:border-green-800">
                                                <h4 className="font-bold text-green-800 dark:text-green-300 mb-1">Recommendation</h4>
                                                <p className="text-sm dark:text-green-100">{comparisonResult.recommendation}</p>
                                            </div>

                                            <div className="overflow-x-auto">
                                                <table className="w-full text-sm">
                                                    <thead>
                                                        <tr className="border-b">
                                                            <th className="text-left font-medium p-2">Vendor</th>
                                                            <th className="text-left font-medium p-2">Score</th>
                                                            <th className="text-left font-medium p-2">Price Ranking</th>
                                                            <th className="text-left font-medium p-2">Strengths</th>
                                                            <th className="text-left font-medium p-2">Weaknesses</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {comparisonResult.comparison_matrix?.map((row: any, i: number) => (
                                                            <tr key={i} className={`border-b ${row.vendor_name === comparisonResult.best_vendor_name ? "bg-accent/50" : ""}`}>
                                                                <td className="p-2 font-medium">{row.vendor_name}</td>
                                                                <td className="p-2 font-bold">{row.score}</td>
                                                                <td className="p-2">{row.price_ranking}</td>
                                                                <td className="p-2 text-green-600 truncate max-w-[150px]" title={row.key_strengths}>{row.key_strengths}</td>
                                                                <td className="p-2 text-red-600 truncate max-w-[150px]" title={row.key_weaknesses}>{row.key_weaknesses}</td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                            </div>
                                        </div>
                                    </CardContent>
                                )}
                            </Card>
                        )}


                        <h3 className="text-lg font-semibold">Individual Analyzed Proposals ({proposals.length})</h3>
                        {proposals.length === 0 ? (
                            <p className="text-zinc-500">No proposals received yet.</p>
                        ) : (
                            <div className="grid gap-4">
                                {proposals.map(p => {
                                    const analysis = p.extracted_data ? parseAnalysis(p.extracted_data) : {};
                                    const vendorName = vendors.find(v => v.id === p.vendor_id)?.name || "Unknown Vendor";

                                    return (
                                        <Card key={p.id} className="border-l-4 border-l-blue-500">
                                            <CardHeader className="pb-2">
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <CardTitle>{vendorName}</CardTitle>
                                                        <CardDescription>AI Score: <span className="font-bold text-foreground">{p.ai_score}/100</span></CardDescription>
                                                    </div>
                                                    <div className="text-right">
                                                        <div className="text-xl font-bold">
                                                            {analysis.extracted_price ? `$${analysis.extracted_price}` : "N/A"}
                                                        </div>
                                                        <div className="text-xs text-zinc-500">
                                                            Timeline: {analysis.extracted_timeline || "Unknown"}
                                                        </div>
                                                    </div>
                                                </div>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="text-sm space-y-2">
                                                    <p className="font-medium">AI Rationale:</p>
                                                    <p className="text-zinc-600 dark:text-zinc-300 italic">{p.ai_rationale}</p>

                                                    {analysis.pros && analysis.pros.length > 0 && (
                                                        <div className="text-green-600 dark:text-green-400">
                                                            <span className="font-bold">Pros:</span> {analysis.pros.join(", ")}
                                                        </div>
                                                    )}
                                                    {analysis.cons && analysis.cons.length > 0 && (
                                                        <div className="text-red-600 dark:text-red-400">
                                                            <span className="font-bold">Cons:</span> {analysis.cons.join(", ")}
                                                        </div>
                                                    )}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
