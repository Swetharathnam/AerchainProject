import { useState, useEffect } from 'react';
import { api, type RFP } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export function RFPDashboard() {
    const [rfps, setRfps] = useState<RFP[]>([]);
    const [vendors, setVendors] = useState<any[]>([]);
    const [selectedRfp, setSelectedRfp] = useState<RFP | null>(null);
    const [selectedVendors, setSelectedVendors] = useState<number[]>([]);
    const [isSending, setIsSending] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        const [rfpData, vendorData] = await Promise.all([
            api.listRFPs(),
            api.listVendors()
        ]);
        setRfps(rfpData);
        setVendors(vendorData);
    };

    const handleSendClick = (rfp: RFP) => {
        setSelectedRfp(rfp);
        setSelectedVendors([]); // Reset selection
    };

    const toggleVendor = (vendorId: number) => {
        setSelectedVendors(prev =>
            prev.includes(vendorId)
                ? prev.filter(id => id !== vendorId)
                : [...prev, vendorId]
        );
    };

    const handleConfirmSend = async () => {
        if (!selectedRfp || !selectedRfp.id) return;
        setIsSending(true);
        try {
            await api.sendRFP(selectedRfp.id, selectedVendors);
            alert(`RFP Sent to ${selectedVendors.length} vendors!`);
            setSelectedRfp(null);
            loadData(); // Refresh status
        } catch (error) {
            console.error("Failed to send RFP", error);
            alert("Failed to send RFP. Check backend logs.");
        } finally {
            setIsSending(false);
        }
    };

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold">RFP Dashboard</h2>

            {/* List of RFPs */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {rfps.map(rfp => (
                    <Card key={rfp.id} className={rfp.status === 'open' ? 'border-green-500' : ''}>
                        <CardHeader>
                            <CardTitle className="text-lg">{rfp.title}</CardTitle>
                            <CardDescription>Status: {rfp.status}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-zinc-500 line-clamp-3">{rfp.description}</p>
                            <div className="mt-2 text-sm font-semibold">
                                Budget: {rfp.budget ? `${rfp.budget} ${rfp.currency}` : "N/A"}
                            </div>
                        </CardContent>
                        <CardFooter>
                            <Button variant="outline" onClick={() => handleSendClick(rfp)}>
                                {rfp.status === 'open' ? 'Send to More' : 'Send to Vendors'}
                            </Button>
                        </CardFooter>
                    </Card>
                ))}
            </div>

            {/* Send Dialog / Selection Area (Simplified as inline conditional card for now) */}
            {selectedRfp && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
                    <Card className="w-full max-w-md bg-white dark:bg-zinc-950">
                        <CardHeader>
                            <CardTitle>Send "{selectedRfp.title}"</CardTitle>
                            <CardDescription>Select vendors to email this RFP to.</CardDescription>
                        </CardHeader>
                        <CardContent className="max-h-[300px] overflow-y-auto space-y-2">
                            {vendors.map(vendor => (
                                <div key={vendor.id} className="flex items-center space-x-2 border p-2 rounded">
                                    <Input
                                        type="checkbox"
                                        className="h-4 w-4"
                                        checked={selectedVendors.includes(vendor.id)}
                                        onChange={() => toggleVendor(vendor.id)}
                                    />
                                    <div className="flex-1">
                                        <p className="font-medium">{vendor.name}</p>
                                        <p className="text-xs text-zinc-500">{vendor.email}</p>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                        <CardFooter className="flex justify-between">
                            <Button variant="ghost" onClick={() => setSelectedRfp(null)}>Cancel</Button>
                            <Button onClick={handleConfirmSend} disabled={isSending || selectedVendors.length === 0}>
                                {isSending ? "Sending..." : `Send to ${selectedVendors.length} Vendors`}
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            )}
        </div>
    );
}
