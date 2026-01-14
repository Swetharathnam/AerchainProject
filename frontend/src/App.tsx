import { RFPForm } from '@/components/rfp-form';
import { VendorManager } from '@/components/vendor-manager';
import { RFPDashboard } from '@/components/rfp-dashboard';
import { ProposalComparison } from '@/components/proposal-comparison';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

function App() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <header className="border-b bg-white dark:bg-zinc-900">
        <div className="container mx-auto flex h-16 items-center px-4">
          <h1 className="text-xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
            Aerchain RFP
          </h1>
        </div>
      </header>
      <main className="container mx-auto p-4 py-10">
        <Tabs defaultValue="rfp" className="w-full">
          <TabsList className="mb-8">
            <TabsTrigger value="rfp">Create RFP</TabsTrigger>
            <TabsTrigger value="vendors">Manage Vendors</TabsTrigger>
            <TabsTrigger value="dashboard">Send RFPs</TabsTrigger>
            <TabsTrigger value="proposals">Compare Proposals</TabsTrigger>
          </TabsList>
          <TabsContent value="rfp">
            <RFPForm />
          </TabsContent>
          <TabsContent value="vendors">
            <VendorManager />
          </TabsContent>
          <TabsContent value="dashboard">
            <RFPDashboard />
          </TabsContent>
          <TabsContent value="proposals">
            <ProposalComparison />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App
