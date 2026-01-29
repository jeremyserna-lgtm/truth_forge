/**
 * Google Cloud Secret Manager Integration
 */

import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

const client = new SecretManagerServiceClient();

/**
 * Get secret from Google Cloud Secret Manager
 */
export async function getSecret(secretName: string): Promise<string> {
    const projectId = process.env.GOOGLE_CLOUD_PROJECT || 'flash-clover-464719-g1';
    const name = `projects/${projectId}/secrets/${secretName}/versions/latest`;

    try {
        const [version] = await client.accessSecretVersion({ name });
        const payload = version.payload?.data?.toString();

        if (!payload) {
            throw new Error(`Secret ${secretName} is empty`);
        }

        return payload;
    } catch (error) {
        console.error(`Failed to get secret ${secretName}:`, error);
        throw error;
    }
}

/**
 * Load all required secrets at startup
 */
export async function loadSecrets() {
    try {
        // Try loading Google_API_Key (this might be your Gemini key)
        const geminiKey = await getSecret('Google_API_Key');
        process.env.GEMINI_API_KEY = geminiKey;

        console.log('✅ Secrets loaded from Google Cloud Secret Manager');

        return {
            geminiApiKey: geminiKey
        };
    } catch (error) {
        console.error('❌ Failed to load secrets from Secret Manager');
        console.log('💡 Falling back to local environment variables if available');

        return {
            geminiApiKey: process.env.GEMINI_API_KEY || ''
        };
    }
}
