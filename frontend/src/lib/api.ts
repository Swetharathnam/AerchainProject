import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface RFP {
    id?: number;
    title: string;
    description: string;
    budget?: number;
    currency?: string;
    status?: string;
    structured_data?: any;
}

export const api = {
    generateRFPStructure: async (naturalLanguageInput: string) => {
        const response = await axios.post(`${API_URL}/rfps/generate`, {
            natural_language_input: naturalLanguageInput
        });
        return response.data;
    },

    createRFP: async (rfpData: RFP) => {
        const response = await axios.post(`${API_URL}/rfps/`, rfpData);
        return response.data;
    },

    listRFPs: async () => {
        const response = await axios.get<RFP[]>(`${API_URL}/rfps/`);
        return response.data;
    },

    healthCheck: async () => {
        const response = await axios.get(`${API_URL}/health`);
        return response.data;
    },

    // Vendor Methods
    createVendor: async (vendorData: { name: string; email: string; contact_person?: string }) => {
        const response = await axios.post(`${API_URL}/vendors/`, vendorData);
        return response.data;
    },

    listVendors: async () => {
        const response = await axios.get<any[]>(`${API_URL}/vendors/`);
        return response.data;
    },

    sendRFP: async (rfpId: number, vendorIds: number[]) => {
        const response = await axios.post(`${API_URL}/rfps/${rfpId}/send`, { vendor_ids: vendorIds });
        return response.data;
    },

    // Proposal Methods
    submitProposal: async (proposalData: { rfp_id: number; vendor_id: number; raw_response: string }) => {
        const response = await axios.post(`${API_URL}/proposals/`, proposalData);
        return response.data;
    },

    listProposals: async (rfpId: number) => {
        const response = await axios.get<any[]>(`${API_URL}/proposals/rfp/${rfpId}`);
        return response.data;
    },

    compareProposals: async (rfpId: number) => {
        const response = await axios.post(`${API_URL}/proposals/compare/${rfpId}`);
        return response.data;
    }
};
