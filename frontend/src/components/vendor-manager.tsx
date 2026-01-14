import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';

const vendorSchema = z.object({
    name: z.string().min(2, "Name must be at least 2 characters."),
    email: z.string().email("Invalid email address."),
    contact_person: z.string().optional(),
});

export function VendorManager() {
    const [vendors, setVendors] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const { register, handleSubmit, reset, formState: { errors } } = useForm<z.infer<typeof vendorSchema>>({
        resolver: zodResolver(vendorSchema),
    });

    const fetchVendors = async () => {
        try {
            const data = await api.listVendors();
            setVendors(data);
        } catch (error) {
            console.error("Failed to fetch vendors", error);
        }
    };

    useEffect(() => {
        fetchVendors();
    }, []);

    const onSubmit = async (data: z.infer<typeof vendorSchema>) => {
        setIsLoading(true);
        try {
            await api.createVendor(data);
            reset();
            fetchVendors(); // Refresh list
        } catch (error) {
            console.error("Failed to create vendor", error);
            alert("Failed to create vendor");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="grid gap-6 md:grid-cols-2">
            {/* Create Vendor Form */}
            <Card>
                <CardHeader>
                    <CardTitle>Add New Vendor</CardTitle>
                    <CardDescription>Register a vendor to send RFPs to.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Vendor Name</Label>
                            <Input id="name" {...register("name")} placeholder="Acme Corp" />
                            {errors.name && <p className="text-sm text-red-500">{errors.name.message}</p>}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="email">Email Address</Label>
                            <Input id="email" type="email" {...register("email")} placeholder="sales@acme.com" />
                            {errors.email && <p className="text-sm text-red-500">{errors.email.message}</p>}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="contact">Contact Person</Label>
                            <Input id="contact" {...register("contact_person")} placeholder="John Doe" />
                        </div>

                        <Button type="submit" disabled={isLoading} className="w-full">
                            {isLoading ? "Adding..." : "Add Vendor"}
                        </Button>
                    </form>
                </CardContent>
            </Card>

            {/* Vendor List */}
            <Card>
                <CardHeader>
                    <CardTitle>Registered Vendors ({vendors.length})</CardTitle>
                    <CardDescription>Vendors available for RFP distribution.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {vendors.length === 0 ? (
                            <p className="text-sm text-zinc-500">No vendors registered yet.</p>
                        ) : (
                            vendors.map((vendor) => (
                                <div key={vendor.id} className="flex items-center justify-between rounded-lg border p-3">
                                    <div>
                                        <p className="font-medium">{vendor.name}</p>
                                        <p className="text-sm text-zinc-500">{vendor.email}</p>
                                    </div>
                                    {vendor.contact_person && (
                                        <span className="text-xs bg-zinc-100 px-2 py-1 rounded dark:bg-zinc-800">
                                            {vendor.contact_person}
                                        </span>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
